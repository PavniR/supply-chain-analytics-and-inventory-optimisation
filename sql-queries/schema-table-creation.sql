CREATE TABLE raw_supply_chain (
    date DATE,
    sku_id VARCHAR(20),
    warehouse_id VARCHAR(20),
    supplier_id VARCHAR(20),
    region VARCHAR(30),
    units_sold INT,
    inventory_level INT,
    supplier_lead_time_days INT,
    reorder_point INT,
    order_quantity INT,
    unit_cost NUMERIC(10,2),
    unit_price NUMERIC(10,2),
    promotion_flag BOOLEAN,
    stockout_flag BOOLEAN,
    revenue NUMERIC(12,2),
    cogs NUMERIC(12,2),
    unit_profit NUMERIC(10,2),
    profit NUMERIC(12,2),
    profit_margin NUMERIC(6,2),
    inventory_value NUMERIC(14,2),
    year INT,
    month INT,
    quarter INT,
    day INT,
    day_of_week INT,
	reorder_needed BOOLEAN,
    inventory_difference INT
);

CREATE TABLE forecast_results (
    date DATE,
    sku_id VARCHAR(20),
    actual_demand INT,
    predicted_demand NUMERIC(10,2)

);

CREATE TABLE inventory_optimization (
    warehouse_id VARCHAR(20),
    sku_id VARCHAR(20),
    current_inventory INT,
    avg_daily_demand NUMERIC(10,2),
    demand_std NUMERIC(10,2),
    lead_time NUMERIC(10,2),
    unit_cost NUMERIC(10,2),
    unit_price NUMERIC(10,2),
    safety_stock NUMERIC(10,2),
    lead_time_demand NUMERIC(10,2),
    recommended_reorder_point NUMERIC(10,2),
    recommended_order_qty NUMERIC(10,2),
    inventory_status VARCHAR(30),
    inventory_gap NUMERIC(10,2),
    excess_units NUMERIC(10,2),
    excess_inventory_value NUMERIC(14,2)
);
