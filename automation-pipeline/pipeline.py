import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")

if not all([HOST, PORT, DATABASE, USER, PASSWORD]):
    raise RuntimeError("Database environment variables are incomplete.")

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

ROOT = Path(__file__).resolve().parent.parent

DATA_PATHS = {
    "raw_supply_chain": ROOT / "data" / "raw_supply_chain.csv",
    "forecast_results": ROOT / "data" / "forecast_results.csv",
    "inventory_optimization": ROOT / "data" / "inventory_optimization.csv",
}

REQUIRED_COLUMNS = {
    "raw_supply_chain": {
        "sku_id",
        "warehouse_id",
        "region",
        "month",
        "units_sold",
        "revenue",
        "profit",
    },
    "forecast_results": {
        "date",
        "sku_id",
        "actual_demand",
        "predicted_demand",
    },
    "inventory_optimization": {
        "sku_id",
        "warehouse_id",
        "current_inventory",
        "avg_daily_demand",
        "lead_time",
        "demand_std",
        "recommended_reorder_point",
        "recommended_order_qty",
        "inventory_status",
    },
}

NON_NEGATIVE_COLUMNS = {
    "raw_supply_chain": ["units_sold", "revenue"],
    "forecast_results": ["actual_demand", "predicted_demand"],
    "inventory_optimization": [
        "current_inventory",
        "avg_daily_demand",
        "lead_time",
        "demand_std",
        "recommended_reorder_point",
        "recommended_order_qty",
    ],
}


def validate_dataset(name: str, dataframe: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS[name] - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"{name}: missing required columns: {sorted(missing_columns)}"
        )

    missing_values = int(dataframe.isna().sum().sum())
    duplicate_rows = int(dataframe.duplicated().sum())

    if missing_values:
        raise ValueError(f"{name}: found {missing_values:,} missing values.")

    if duplicate_rows:
        raise ValueError(f"{name}: found {duplicate_rows:,} duplicate rows.")

    for column in NON_NEGATIVE_COLUMNS[name]:
        if (dataframe[column] < 0).any():
            raise ValueError(
                f"{name}: column '{column}' contains negative values."
            )

    if name == "inventory_optimization":
        valid_statuses = {
            "Healthy",
            "Overstock",
            "Reorder Immediately",
        }

        invalid_statuses = (
            set(dataframe["inventory_status"]) - valid_statuses
        )

        if invalid_statuses:
            raise ValueError(
                f"{name}: invalid inventory statuses: "
                f"{sorted(invalid_statuses)}"
            )


def upload_to_staging(datasets: dict[str, pd.DataFrame]) -> None:
    print("Uploading validated datasets to staging tables...")

    for table_name, dataframe in datasets.items():
        dataframe.to_sql(
            f"{table_name}_staging",
            engine,
            if_exists="replace",
            index=False,
        )


def swap_tables(table_names: list[str]) -> None:
    print("Refreshing production tables atomically...")

    with engine.begin() as connection:
        for table_name in table_names:
            staging_table = f"{table_name}_staging"

            connection.execute(
                text(f'DROP TABLE IF EXISTS "{table_name}"')
            )

            connection.execute(
                text(
                    f'ALTER TABLE "{staging_table}" '
                    f'RENAME TO "{table_name}"'
                )
            )


def verify_upload(expected_counts: dict[str, int]) -> None:
    print("Verifying refreshed tables...")

    with engine.connect() as connection:
        for table_name, expected_count in expected_counts.items():
            actual_count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar_one()

            if actual_count != expected_count:
                raise RuntimeError(
                    f"{table_name}: expected {expected_count:,} rows, "
                    f"found {actual_count:,}."
                )

            print(f"{table_name}: {actual_count:,} rows verified")


def main() -> None:
    print("Reading datasets...")

    datasets = {
        table_name: pd.read_csv(path)
        for table_name, path in DATA_PATHS.items()
    }

    print("Checking data quality...")

    for table_name, dataframe in datasets.items():
        print(f"{table_name}: {len(dataframe):,} rows")
        validate_dataset(table_name, dataframe)

    upload_to_staging(datasets)
    swap_tables(list(datasets))

    verify_upload(
        {
            name: len(dataframe)
            for name, dataframe in datasets.items()
        }
    )

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()