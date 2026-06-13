CREATE TABLE olist.mart_orders AS
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Задержка доставки в днях (положительное = опоздание)
    EXTRACT(DAY FROM (
        o.order_delivered_customer_date - o.order_estimated_delivery_date
    )) AS delivery_delay_days,

    -- Покупатель
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    -- Финансы
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_value,

    -- Товар
    p.product_id,
    COALESCE(ct.product_category_name_english, p.product_category_name) AS category,

    -- Продавец
    s.seller_id,
    s.seller_state,

    -- Отзыв
    r.review_score

FROM olist.orders o
LEFT JOIN olist.customers c         ON o.customer_id = c.customer_id
LEFT JOIN olist.order_items oi      ON o.order_id = oi.order_id
LEFT JOIN olist.products p          ON oi.product_id = p.product_id
LEFT JOIN olist.category_translation ct ON p.product_category_name = ct.product_category_name
LEFT JOIN olist.sellers s           ON oi.seller_id = s.seller_id
LEFT JOIN olist.order_reviews r     ON o.order_id = r.order_id;

-- Индексы для быстрых запросов
CREATE INDEX idx_mart_state    ON olist.mart_orders(customer_state);
CREATE INDEX idx_mart_category ON olist.mart_orders(category);
CREATE INDEX idx_mart_date     ON olist.mart_orders(order_purchase_timestamp);