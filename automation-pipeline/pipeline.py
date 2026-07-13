import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


# Load Environment Variables


load_dotenv()

HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")


# Database Connection ---------------------------------------------------


engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

print("Connected to PostgreSQL")


# File Paths ---------------------------------------------------


ROOT = Path(__file__).resolve().parent.parent

raw_path = ROOT / "data" / "raw_supply_chain.csv"
forecast_path = ROOT / "data" / "forecast_results.csv"
inventory_path = ROOT / "data" / "inventory_optimization.csv"


# Read CSVs ---------------------------------------------------


print("\nReading datasets...")

raw = pd.read_csv(raw_path)
forecast = pd.read_csv(forecast_path)
inventory = pd.read_csv(inventory_path)


# Data Validation ---------------------------------------------------


print("Checking data quality...")

for name, df in {
    "Raw Supply Chain": raw,
    "Forecast": forecast,
    "Inventory": inventory
}.items():

    print(f"\n{name}")
    print(f"Rows : {len(df):,}")
    print(f"Missing Values : {df.isna().sum().sum()}")
    print(f"Duplicate Rows : {df.duplicated().sum()}")


# Upload Tables ---------------------------------------------------


print("\nUploading tables...")

raw.to_sql(
    "raw_supply_chain",
    engine,
    if_exists="replace",
    index=False
)
forecast.to_sql(
    "forecast_results",
    engine,
    if_exists="replace",
    index=False
)
inventory.to_sql(
    "inventory_optimization",
    engine,
    if_exists="replace",
    index=False
)

print("Tables uploaded successfully.")


# Verify Upload ---------------------------------------------------


print("\nVerifying upload...")

with engine.connect() as conn:

    raw_rows = conn.execute(
        text("SELECT COUNT(*) FROM raw_supply_chain")
    ).scalar()

    forecast_rows = conn.execute(
        text("SELECT COUNT(*) FROM forecast_results")
    ).scalar()

    inventory_rows = conn.execute(
        text("SELECT COUNT(*) FROM inventory_optimization")
    ).scalar()

print("\nVerification Complete")
print(f"Raw Supply Chain : {raw_rows:,}")
print(f"Forecast Results : {forecast_rows:,}")
print(f"Inventory Optimization : {inventory_rows:,}")
print("\nPipeline Finished Successfully")