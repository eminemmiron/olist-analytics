-- 1. Пропуски в ключевых полях витрины
SELECT
    COUNT(*)                                              AS total_rows,
    COUNT(*) FILTER (WHERE order_status IS NULL)          AS null_status,
    COUNT(*) FILTER (WHERE order_purchase_timestamp IS NULL) AS null_purchase_date,
    COUNT(*) FILTER (WHERE price IS NULL)                 AS null_price,
    COUNT(*) FILTER (WHERE review_score IS NULL)          AS null_review,
    COUNT(*) FILTER (WHERE category IS NULL)              AS null_category
FROM olist.mart_orders;

-- 2. Дубликаты order_id + product_id (один заказ, один товар)
SELECT order_id, product_id, COUNT(*) AS cnt
FROM olist.mart_orders
GROUP BY order_id, product_id
HAVING COUNT(*) > 1
LIMIT 20;

-- 3. Аномалии в ценах
SELECT
    MIN(price)  AS min_price,
    MAX(price)  AS max_price,
    AVG(price)  AS avg_price,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY price) AS p99_price
FROM olist.mart_orders;

-- 4. Статусы заказов — распределение
SELECT order_status, COUNT(*) AS cnt
FROM olist.mart_orders
GROUP BY order_status
ORDER BY cnt DESC;

-- 5. Временной диапазон данных
SELECT
    MIN(order_purchase_timestamp) AS first_order,
    MAX(order_purchase_timestamp) AS last_order
FROM olist.mart_orders;