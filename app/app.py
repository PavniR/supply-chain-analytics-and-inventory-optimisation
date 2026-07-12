import streamlit as st

st.set_page_config(
    page_title="Supply Chain Analytics Platform",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Supply Chain Analytics Platform")

st.markdown("""
An end-to-end supply chain analytics solution designed to support inventory decisions through
data analytics, SQL reporting, and interactive business dashboards. The project transforms
raw operational data into actionable insights, helping identify overstocking, optimize
replenishment decisions, and monitor warehouse performance.
""")

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Warehouses", "5")
    st.metric("SKUs Analysed", "50")

with c2:
    st.metric("Forecast MAE", "5.46")
    st.metric("Overstock Rate", "78%")

with c3:
    st.metric("Database", "PostgreSQL")
    st.metric("Dashboard", "Streamlit")

st.divider()

st.subheader("summary")

st.markdown("""
- Identified overstocked and understocked inventory across warehouses.
- Generated reorder recommendations using inventory optimization metrics.
- Monitored revenue, profitability, warehouse performance, and regional trends.
- Supports operational decision-making through interactive analytics and SQL reporting.
""")

st.info("📌 Use the navigation panel on the left to explore the Dashboard, Inventory Optimizer, and SQL Analytics modules.")
