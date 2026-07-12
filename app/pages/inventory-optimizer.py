import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import run_query

st.set_page_config(
    page_title="Inventory Optimizer",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Inventory Optimizer")
st.caption("Simulate inventory decisions and generate replenishment recommendations.")


# LOAD DATA -----------------------------------------------


inventory = run_query("""
SELECT *
FROM inventory_optimization
ORDER BY warehouse_id, sku_id
""")


# SIDEBAR -----------------------------------------------


st.sidebar.header("Filters")

warehouse = st.sidebar.selectbox(
    "Warehouse",
    sorted(inventory["warehouse_id"].unique())
)

status_filter = st.sidebar.selectbox(
    "Inventory Status",
    ["All","Healthy","Overstock","Reorder Immediately"]
)

filtered_inventory = inventory[
    inventory["warehouse_id"] == warehouse
].copy()

if status_filter != "All":
    filtered_inventory = filtered_inventory[
        filtered_inventory["inventory_status"] == status_filter
    ]

if filtered_inventory.empty:
    st.warning("No SKUs found for the selected Warehouse and Status.")
    st.stop()

sku = st.sidebar.selectbox(
    "SKU",
    sorted(filtered_inventory["sku_id"].unique())
)

row = filtered_inventory[
    filtered_inventory["sku_id"] == sku
].iloc[0]


# USER INPUTS -----------------------------------------------


st.subheader("Modify Inventory Parameters")

left,right = st.columns(2)

with left:

    current_inventory = st.number_input(
        "Current Inventory",
        min_value=0,
        value=int(row.current_inventory),
        step=1
    )

    avg_daily_demand = st.number_input(
        "Average Daily Demand",
        min_value=0,
        value=int(row.avg_daily_demand),
        step=1
    )

with right:

    lead_time = st.number_input(
        "Lead Time (Days)",
        min_value=1,
        value=int(row.lead_time),
        step=1
    )

    demand_std = st.number_input(
        "Demand Standard Deviation",
        min_value=0,
        value=int(row.demand_std),
        step=1
    )


# CALCULATIONS -----------------------------------------------


z = 1.65

safety_stock = z * demand_std * (lead_time ** 0.5)

lead_time_demand = avg_daily_demand * lead_time

reorder_point = lead_time_demand + safety_stock

recommended_order = max(
    0,
    reorder_point - current_inventory
)

inventory_gap = current_inventory - reorder_point

if current_inventory < reorder_point:

    status = "🔴 Reorder Immediately"

elif current_inventory > reorder_point * 1.5:

    status = "🟠 Overstock"

else:

    status = "🟢 Healthy"


# KPI CARDS -----------------------------------------------


st.divider()

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Safety Stock",
    f"{safety_stock:.0f}"
)

c2.metric(
    "Lead Time Demand",
    f"{lead_time_demand:.0f}"
)

c3.metric(
    "Reorder Point",
    f"{reorder_point:.0f}"
)

c4.metric(
    "Recommended Order",
    f"{recommended_order:.0f}"
)


# INVENTORY POSITION -----------------------------------------------


st.divider()

st.subheader("Inventory Position")

progress = min(
    current_inventory / max(reorder_point,1),
    2
)

st.progress(progress/2)

col1,col2 = st.columns(2)

with col1:

    st.metric(
        "Current Inventory",
        f"{current_inventory} units"
    )

with col2:

    st.metric(
        "Recommended ROP",
        f"{reorder_point:.0f} units"
    )


# RECOMMENDATION PANEL -----------------------------------------------


st.divider()

st.subheader("📌 Inventory Recommendation")

if status == "🔴 Reorder Immediately":

    st.error(f"""
### Immediate Action Required

Current inventory is **below** the calculated reorder point.

**Recommended Order Quantity:** **{recommended_order:.0f} units**

This SKU has a **high stockout risk**.

**Suggested Action**
- Place replenishment order immediately.
- Monitor sales closely until inventory is restored.
""")

elif status == "🟠 Overstock":

    st.warning(f"""
### Overstock Detected

Current inventory exceeds the optimal inventory level.

**Excess Inventory:** **{inventory_gap:.0f} units**

**Suggested Action**
- Reduce future procurement.
- Consider transferring inventory to another warehouse.
- Include this SKU in promotional campaigns.
""")

else:

    st.success("""
### Healthy Inventory

Inventory level is within the recommended range.

No replenishment is required at the moment.

Continue monitoring demand trends.
""")


# INVENTORY SUMMARY -----------------------------------------------


st.divider()

st.subheader("📋 Inventory Summary")

summary = filtered_inventory[
    [
        "sku_id",
        "current_inventory",
        "recommended_reorder_point",
        "recommended_order_qty",
        "inventory_status"
    ]
].copy()

summary.columns = [
    "SKU",
    "Current Inventory",
    "Reorder Point",
    "Recommended Order",
    "Status"
]

summary = summary.sort_values(
    by="Status",
    ascending=False
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# QUICK STATS -----------------------------------------------


st.divider()

st.subheader("📊 Warehouse Summary")

c1, c2, c3 = st.columns(3)

healthy = len(
    filtered_inventory[
        filtered_inventory["inventory_status"] == "Healthy"
    ]
)

overstock = len(
    filtered_inventory[
        filtered_inventory["inventory_status"] == "Overstock"
    ]
)

reorder = len(
    filtered_inventory[
        filtered_inventory["inventory_status"] == "Reorder Immediately"
    ]
)

c1.metric(
    "🟢 Healthy",
    healthy
)

c2.metric(
    "🟠 Overstock",
    overstock
)

c3.metric(
    "🔴 Reorder",
    reorder
)


# DOWNLOAD REPORT -----------------------------------------------


st.divider()

csv = summary.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Inventory Summary",
    csv,
    "inventory_summary.csv",
    "text/csv"
)


# FOOTER -----------------------------------------------

st.caption(
    "Inventory recommendations are generated using the calculated "
    "Reorder Point (ROP) and Safety Stock methodology."
)