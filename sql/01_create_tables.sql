CREATE SCHEMA IF NOT EXISTS olist;

CREATE TABLE olist.customers (
    customer_id           		VARCHAR PRIMARY KEY,
    customer_unique_id    		VARCHAR,
    customer_zip_code_prefix    VARCHAR,
    customer_city         		VARCHAR,
    customer_state        		CHAR(2)
);

CREATE TABLE olist.geolocation (
    geolocation_zip_code_prefix VARCHAR,
    geolocation_lat       		NUMERIC,
    geolocation_lng       		NUMERIC,
    geolocation_city      		VARCHAR,
    geolocation_state     		CHAR(2)
);

CREATE TABLE olist.orders (
    order_id                      VARCHAR PRIMARY KEY,
    customer_id                   VARCHAR REFERENCES olist.customers(customer_id),
    order_status                  VARCHAR,
    order_purchase_timestamp      TIMESTAMP,
    order_approved_at             TIMESTAMP,
    order_delivered_carrier_date  TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE olist.order_items (
    order_id             VARCHAR REFERENCES olist.orders(order_id),
    order_item_id        INTEGER,
    product_id           VARCHAR,
    seller_id            VARCHAR,
    shipping_limit_date  TIMESTAMP,
    price                NUMERIC(10,2),
    freight_value        NUMERIC(10,2),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE olist.order_payments (
    order_id              VARCHAR REFERENCES olist.orders(order_id),
    payment_sequential    INTEGER,
    payment_type          VARCHAR,
    payment_installments  INTEGER,
    payment_value         NUMERIC(10,2),
    PRIMARY KEY (order_id, payment_sequential)
);


CREATE TABLE olist.order_reviews (
    review_id                 VARCHAR,
    order_id                  VARCHAR REFERENCES olist.orders(order_id),
    review_score              SMALLINT,
    review_comment_title      TEXT,
    review_comment_message    TEXT,
    review_creation_date      TIMESTAMP,
    review_answer_timestamp   TIMESTAMP,
    PRIMARY KEY (review_id, order_id)
);

CREATE TABLE olist.products (
    product_id                 VARCHAR PRIMARY KEY,
    product_category_name      VARCHAR,
    product_name_length        INTEGER,
    product_description_length INTEGER,
    product_photos_qty         INTEGER,
    product_weight_g           INTEGER,
    product_length_cm          INTEGER,
    product_height_cm          INTEGER,
    product_width_cm           INTEGER
);


CREATE TABLE olist.sellers (
    seller_id         		VARCHAR PRIMARY KEY,
    seller_zip_code_prefix  VARCHAR,
    seller_city       		VARCHAR,
    seller_state      		CHAR(2)
);


CREATE TABLE olist.category_translation (
    product_category_name          VARCHAR PRIMARY KEY,
    product_category_name_english  VARCHAR
);