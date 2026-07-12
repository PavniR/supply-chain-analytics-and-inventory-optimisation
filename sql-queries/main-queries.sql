--top 10 revenue generating SKUs
SELECT sku_id, ROUND(SUM(revenue),2) AS total_revenue,
SUM(units_sold) AS total_units
FROM raw_supply_chain
GROUP BY sku_id
ORDER BY total_revenue DESC
LIMIT 10;

--revenue by warehouse
SELECT warehouse_id, ROUND(SUM(revenue),2) AS revenue,
ROUND(SUM(profit),2) AS profit
FROM raw_supply_chain
GROUP BY warehouse_id
ORDER BY revenue DESC;

--revenue by region
SELECT region, ROUND(SUM(revenue),2) AS revenue,
ROUND(SUM(profit),2) AS profit
FROM raw_supply_chain
GROUP BY region
ORDER BY revenue DESC;

--monthly sales trend
SELECT month, SUM(units_sold) AS units,
ROUND(SUM(revenue),2) AS revenue
FROM raw_supply_chain
GROUP BY month
ORDER BY month;

--warehouse with highest excessive inventory
SELECT warehouse_id, ROUND(SUM(excess_inventory_value),2) AS excess_value
FROM inventory_optimization
GROUP BY warehouse_id
ORDER BY excess_value DESC;

--overstock locations (warehouse-sku)
SELECT COUNT(sku_id)
FROM inventory_optimization
WHERE inventory_status='Overstock';

--overstock rate:
SELECT ROUND(100.0*COUNT(*) FILTER (WHERE inventory_status='Overstock')/
COUNT(*),1) AS overstock_rate
FROM inventory_optimization;

--SKUs that need immediate order
SELECT sku_id, warehouse_id, current_inventory, recommended_reorder_point, recommended_order_qty
FROM inventory_optimization
WHERE inventory_status='Reorder Immediately'
ORDER BY recommended_order_qty DESC;

--inventory status count
SELECT inventory_status, COUNT(*) AS total
FROM inventory_optimization
GROUP BY inventory_status;

--ranking SKUs by revenue:
SELECT sku_id, SUM(revenue) AS revenue,
RANK() OVER(ORDER BY SUM(revenue) DESC) AS revenue_rank
FROM raw_supply_chain
GROUP BY sku_id;

--running monthly revenue:
SELECT month, SUM(revenue) AS revenue,
SUM(SUM(revenue)) OVER(ORDER BY month) AS cumulative_revenue
FROM raw_supply_chain
GROUP BY month
ORDER BY month;

--total profit per SKU year-long
WITH sku_profit AS(
SELECT sku_id,SUM(profit) AS total_profit
FROM raw_supply_chain
GROUP BY sku_id)

SELECT *
FROM sku_profit
WHERE total_profit>(SELECT AVG(total_profit) FROM sku_profit);


--forecast accuracy-MAE
SELECT
ROUND(AVG(ABS(actual_demand-predicted_demand)),2) AS MAE
FROM forecast_results;

--largest forecast errors
SELECT
date,
sku_id,
actual_demand,
predicted_demand,
ABS(actual_demand-predicted_demand) AS error
FROM forecast_results
ORDER BY error DESC
LIMIT 20;