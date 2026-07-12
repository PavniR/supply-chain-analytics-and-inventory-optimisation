import streamlit as st
import sys
from pathlib import Path
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import run_query

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

st.title("📊 Supply Chain Dashboard")


# SIDEBAR FILTERS -----------------------------------------------


with st.sidebar:

    st.header("Filters")

    warehouse_filter = st.selectbox(
        "Warehouse",
        ["All"] + list(
            run_query("""
                SELECT DISTINCT warehouse_id
                FROM raw_supply_chain
                ORDER BY warehouse_id
            """)["warehouse_id"]
        )
    )

    region_filter = st.selectbox(
        "Region",
        ["All"] + list(
            run_query("""
                SELECT DISTINCT region
                FROM raw_supply_chain
                ORDER BY region
            """)["region"]
        )
    )


# SQL FILTER CLAUSE -----------------------------------------------


filter_clause = ""

if warehouse_filter != "All":
    filter_clause += f" AND warehouse_id = '{warehouse_filter}'"

if region_filter != "All":
    filter_clause += f" AND region = '{region_filter}'"


# KPIs -----------------------------------------------


total_revenue = run_query(f"""
SELECT SUM(revenue)
FROM raw_supply_chain
WHERE 1=1
{filter_clause}
""").iloc[0,0]

total_profit = run_query(f"""
SELECT SUM(profit)
FROM raw_supply_chain
WHERE 1=1
{filter_clause}
""").iloc[0,0]

forecast_mae = run_query("""
SELECT ROUND(AVG(ABS(actual_demand-predicted_demand)),2)
FROM forecast_results
""").iloc[0,0]

overstock = run_query("""
SELECT ROUND(
100.0*COUNT(*) FILTER (WHERE inventory_status='Overstock')
/COUNT(*),1)
FROM inventory_optimization
""").iloc[0,0]

c1,c2,c3,c4 = st.columns(4)

c1.metric("💰 Revenue",f"${total_revenue:,.0f}")
c2.metric("💵 Profit",f"${total_profit:,.0f}")
c3.metric("📈 Forecast MAE",forecast_mae)
c4.metric("📦 Overstock",f"{overstock}%")


# MONTHLY REVENUE -----------------------------------------------


trend = run_query(f"""
SELECT
month,
SUM(revenue) revenue
FROM raw_supply_chain
WHERE 1=1
{filter_clause}
GROUP BY month
ORDER BY month
""")

st.markdown("### Monthly Revenue")

fig = px.area(
    trend,
    x="month",
    y="revenue",
    color_discrete_sequence=["#5B8FF9"]
)

fig.update_layout(
    height=260,
    margin=dict(l=10,r=10,t=10,b=10)
)

st.plotly_chart(fig,use_container_width=True)


# WAREHOUSE + INVENTORY -----------------------------------------------

left,right = st.columns(2)

warehouse = run_query(f"""
SELECT
warehouse_id,
SUM(revenue) revenue
FROM raw_supply_chain
WHERE 1=1
GROUP BY warehouse_id
ORDER BY revenue DESC
""")

with left:

    st.markdown("### Revenue by Warehouse")

    fig = px.bar(
        warehouse,
        x="warehouse_id",
        y="revenue",
        color_discrete_sequence=["#89D3E6"]
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10,r=10,t=10,b=10),
        showlegend=False
    )

    st.plotly_chart(fig,use_container_width=True)

inventory = run_query("""
SELECT
inventory_status,
COUNT(*) total
FROM inventory_optimization
GROUP BY inventory_status
""")

with right:

    st.markdown("### 📦 Inventory Status")

    fig = px.bar(
        inventory,
        x="inventory_status",
        y="total",
        color_discrete_sequence=["#5DADE2"]
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10,r=10,t=10,b=10),
        showlegend=False
    )

    st.plotly_chart(fig,use_container_width=True)

# ==========================================================
# TOP SKU + REGION
# ==========================================================

left,right = st.columns(2)

topsku = run_query(f"""
SELECT
sku_id,
SUM(revenue) revenue
FROM raw_supply_chain
WHERE 1=1
{filter_clause}
GROUP BY sku_id
ORDER BY revenue DESC
LIMIT 10
""")

with left:

    st.markdown("### Top Revenue SKUs")

    fig = px.bar(
        topsku.sort_values("revenue"),
        x="revenue",
        y="sku_id",
        orientation="h",
        color_discrete_sequence=["#434C51"]
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis_title="Revenue ($)",
        yaxis_title=""
    )

    st.plotly_chart(fig,use_container_width=True)

region = run_query(f"""
SELECT
region,
SUM(revenue) revenue
FROM raw_supply_chain
WHERE 1=1
{filter_clause}
GROUP BY region
ORDER BY revenue DESC
""")

with right:

    st.markdown("### Revenue by Region")

    fig = px.pie(
        region,
        names="region",
        values="revenue",
        hole=0.45,
        color_discrete_sequence=[
            "#5B8FF9",
            "#8EC5FC",
            "#A0D8EF",
            "#C7E9F1"
        ]
    )

    fig.update_traces(
        textinfo="percent+label"
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10,r=10,t=10,b=10)
    )

    st.plotly_chart(fig,use_container_width=True)
