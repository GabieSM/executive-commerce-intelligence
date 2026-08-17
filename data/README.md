# Data

## Executive Commerce Intelligence Platform

### 1. Dataset

This project uses the **Brazilian E-Commerce Public Dataset by Olist**, a public and anonymized Brazilian marketplace dataset.

The downloaded source consists of nine CSV files covering marketplace transactions, customers, products, sellers, payments, reviews, and geographic information.

The data available in this project contains order activity from:

> **2016-09-04 to 2018-10-17**

The dataset is used exclusively as the source for an independent portfolio analytics project.

The business context, stakeholder requirements, analytical models, KPIs, dashboards, and recommendations developed in this repository are simulated and do not represent current Olist operations or internal management practices.

---

## 2. Raw Data Policy

Original source files are stored locally under:

`data/raw/`

The directory is excluded from Git version control through `.gitignore`.

Raw source files must not be manually modified.

The intended data flow is:

> **Source Dataset → Local Raw Files → PostgreSQL Raw Layer → dbt Staging → Warehouse → Analytical Marts → Analytics & BI**

Cleaning, standardization, type conversion, deduplication, enrichment, and business logic must occur downstream from the original raw files.

---

## 3. Source Data Inventory

Initial profiling of the downloaded files produced the following inventory.

| Source File | Rows | Columns | Business Entity | Validated / Observed Grain |
|---|---:|---:|---|---|
| `olist_orders_dataset.csv` | 99,441 | 8 | Orders | One row per `order_id` |
| `olist_customers_dataset.csv` | 99,441 | 5 | Customers | One row per `customer_id` |
| `olist_order_items_dataset.csv` | 112,650 | 7 | Order Items | One row per `order_id` + `order_item_id` |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | Payments | Multiple payment records may exist per order |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | Reviews | Multiple review records may exist per order |
| `olist_products_dataset.csv` | 32,951 | 9 | Products | One row per `product_id` |
| `olist_sellers_dataset.csv` | 3,095 | 4 | Sellers | One row per `seller_id` |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | Geolocation | Multiple observations may exist per ZIP-code prefix |
| `product_category_name_translation.csv` | 71 | 2 | Category Translation | One row per translated Portuguese category |

---

## 4. Validated Source Keys & Cardinalities

### Orders

`olist_orders_dataset.csv` contains:

- 99,441 rows;
- 99,441 distinct `order_id` values;
- no duplicated `order_id`.

Therefore:

> **Validated grain: one row per order**

Observed order statuses:

| Order Status | Orders |
|---|---:|
| delivered | 96,478 |
| shipped | 1,107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

The existence of multiple order statuses means that the definition of a **valid analytical order** must be established explicitly for each relevant KPI.

---

### Customers

`olist_customers_dataset.csv` contains:

- 99,441 distinct `customer_id` values;
- 96,096 distinct `customer_unique_id` values.

A total of **2,997 persistent customer identifiers occur in more than one customer record**, with the most frequently occurring `customer_unique_id` appearing in 17 records.

This confirms that:

- `customer_id` represents the transactional customer relationship used by orders;
- `customer_unique_id` must be used when analyzing persistent customer behavior across orders.

Therefore, repeat purchasing, cohorts, retention, purchase frequency, and customer segmentation must use `customer_unique_id`.

---

### Order Items

`olist_order_items_dataset.csv` contains:

- 112,650 rows;
- 98,666 distinct orders;
- no duplicate combinations of `order_id` + `order_item_id`.

Therefore:

> **Validated grain: one row per order-item position**

There are **775 orders without order-item records**.

Their statuses are:

| Status | Orders without Items |
|---|---:|
| unavailable | 603 |
| canceled | 164 |
| created | 5 |
| invoiced | 2 |
| shipped | 1 |

This relationship will be considered when defining commercial populations such as GMV and Items Sold.

---

### Payments

`olist_order_payments_dataset.csv` contains:

- 103,886 payment records;
- 99,440 distinct orders represented in the payment dataset.

An order may contain multiple payment records, with the observed maximum being **29 payment records for a single order**.

One order in the Orders dataset has no corresponding payment record.

The order is classified as `delivered`.

Therefore, payment data must be aggregated to an appropriate grain before being combined with order-item-level measures.

Direct joins between payments and order items may create fan-out duplication.

---

### Reviews

`olist_order_reviews_dataset.csv` contains:

- 99,224 review records;
- 98,673 distinct `order_id` values;
- up to **3 review records for a single order**;
- 547 orders with more than one review record.

Therefore:

> **The relationship between Orders and Reviews is not strictly one-to-one.**

Review logic must define which review grain is required before review measures are added to order-level analytical models.

---

### Products

`olist_products_dataset.csv` contains:

- 32,951 rows;
- 32,951 distinct `product_id` values.

Therefore:

> **Validated grain: one row per product**

The dataset contains:

- 610 products without `product_category_name`;
- 2 products without physical dimension or weight information.

There are 73 non-null Portuguese product categories represented in the Products dataset.

---

### Product Category Translation

The translation dataset contains:

- 71 rows;
- 71 unique Portuguese category names.

Two categories appearing in the Products dataset do not have a corresponding English translation:

- `pc_gamer`
- `portateis_cozinha_e_preparadores_de_alimentos`

These categories must remain identifiable during transformation rather than being silently removed by an inner join.

---

### Sellers

`olist_sellers_dataset.csv` contains:

- 3,095 rows;
- 3,095 distinct `seller_id` values.

Therefore:

> **Validated grain: one row per seller**

---

### Geolocation

`olist_geolocation_dataset.csv` contains:

- 1,000,163 rows;
- 19,015 distinct ZIP-code prefixes;
- 261,831 fully duplicated rows.

The source therefore does not represent a one-row-per-ZIP reference table.

A direct join between customers or sellers and the raw geolocation dataset could multiply records and distort analytical measures.

A standardized geographic model must therefore be created before geolocation is used for enrichment.

---

## 5. Validated Referential Integrity

The following core source relationships were tested against the downloaded files:

| Relationship | Orphan Records |
|---|---:|
| Orders → Customers (`customer_id`) | 0 |
| Order Items → Orders (`order_id`) | 0 |
| Order Items → Products (`product_id`) | 0 |
| Order Items → Sellers (`seller_id`) | 0 |
| Payments → Orders (`order_id`) | 0 |
| Reviews → Orders (`order_id`) | 0 |

No orphan foreign-key values were identified in these core relationships during initial profiling.

---

## 6. Important Grain Relationships

The source model contains multiple one-to-many relationships.

```text
customers
    │
    │ customer_id
    ▼
orders
    │
    ├──────────────► order_items
    │                    │
    │                    ├──► products
    │                    └──► sellers
    │
    ├──────────────► payments
    │
    └──────────────► reviews

```text
Customer ID        → one customer record
Customer Unique ID → potentially multiple customer records

Order              → potentially multiple order items
Order              → potentially multiple payments
Order              → potentially multiple reviews

Product            → one product record
Seller             → one seller record

ZIP Prefix         → potentially many geolocation records
```

These cardinalities must be respected when designing the analytical warehouse.

---

## 7. Known Source Data Quality Conditions

Initial profiling identified several conditions that require explicit transformation or analytical treatment:

- multiple order statuses;
- orders without order items;
- one delivered order without payment information;
- multiple payments per order;
- multiple reviews for some orders;
- missing product categories;
- missing product physical attributes;
- product categories without English translation;
- high duplication within the geolocation dataset;
- nullable operational timestamps;
- finite observation window affecting customer lifecycle analysis.

These conditions must not be silently corrected or removed.

Treatment rules will be documented in staging models, KPI definitions, and data-quality tests.

---

## 8. Validation Status

Initial structural profiling has been completed.

Validated characteristics currently include:

- source row and column counts;
- primary identifier uniqueness;
- important table grains;
- core relationship cardinalities;
- core referential integrity;
- order-status distribution;
- customer identifier behavior;
- review multiplicity;
- payment multiplicity;
- major missing-value patterns;
- geographic duplication;
- product-category translation coverage.

Additional profiling is still required for:

- timestamp consistency;
- monetary distributions and anomalies;
- delivery-time distributions;
- freight distributions;
- payment-value reconciliation;
- review-score distributions;
- geographic standardization;
- business-rule populations;
- outlier detection.

---

## 9. Local Directory Structure

```text
data/
├── README.md
└── raw/
    ├── olist_customers_dataset.csv
    ├── olist_geolocation_dataset.csv
    ├── olist_order_items_dataset.csv
    ├── olist_order_payments_dataset.csv
    ├── olist_order_reviews_dataset.csv
    ├── olist_orders_dataset.csv
    ├── olist_products_dataset.csv
    ├── olist_sellers_dataset.csv
    └── product_category_name_translation.csv
```

Only `README.md` is version-controlled.

The contents of `data/raw/` remain local and are intentionally excluded from the public repository.
