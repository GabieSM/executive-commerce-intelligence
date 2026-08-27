# Executive Commerce Intelligence Platform — Physical Architecture

## 1. Purpose

This document defines the physical data-platform architecture used to implement the Executive Commerce Intelligence Platform.

It translates the validated logical dimensional model into concrete PostgreSQL schemas, dbt layers, ingestion responsibilities, naming conventions, and materialization strategies.

The architecture follows the logical flow:

RAW
↓
STAGING
↓
CORE
↓
INTERMEDIATE
↓
MARTS
↓
ANALYTICS

The design prioritizes:

- reproducibility;
- source traceability;
- explicit transformation ownership;
- grain preservation;
- analytical fanout protection;
- testability;
- maintainability;
- separation between ingestion and analytics engineering.

---

# 2. Technology Responsibilities

The platform uses the following core technologies.

| Technology | Primary Responsibility |
|---|---|
| Python | Source ingestion and ingestion-level validation |
| PostgreSQL | Physical analytical database and warehouse storage |
| dbt | Transformation, dimensional modeling, business logic, testing, documentation |
| Docker | Reproducible PostgreSQL infrastructure |
| SQL | Warehouse transformations and analytical validation |
| Python / pandas | Statistical and exploratory analysis |
| Tableau Public | Business-intelligence visualization |
| Git / GitHub | Version control and project reproducibility |

A clear ownership boundary will be maintained:

> Python owns ingestion into RAW.

> dbt owns transformations from STAGING onward.

---

# 3. PostgreSQL Database

The local analytical PostgreSQL instance will contain one project database.

Planned database:

`executive_commerce`

The database will contain five governed schemas:

- `raw`
- `staging`
- `core`
- `intermediate`
- `marts`

Conceptually:

PostgreSQL
└── executive_commerce
    ├── raw
    ├── staging
    ├── core
    ├── intermediate
    └── marts

Each schema has a distinct responsibility.

---

# 4. RAW Schema

## Purpose

The `raw` schema contains source data loaded from the original Olist CSV files.

RAW represents the closest database copy of the source files.

No business logic should be applied in this layer.

## Transformation Owner

> Python ingestion pipeline.

dbt must treat RAW tables as sources rather than transformation models.

## Physical Object Type

> PostgreSQL tables.

## Planned Tables

| Source File | RAW Table |
|---|---|
| `olist_customers_dataset.csv` | `raw.olist_customers` |
| `olist_orders_dataset.csv` | `raw.olist_orders` |
| `olist_order_items_dataset.csv` | `raw.olist_order_items` |
| `olist_order_payments_dataset.csv` | `raw.olist_order_payments` |
| `olist_order_reviews_dataset.csv` | `raw.olist_order_reviews` |
| `olist_products_dataset.csv` | `raw.olist_products` |
| `olist_sellers_dataset.csv` | `raw.olist_sellers` |
| `olist_geolocation_dataset.csv` | `raw.olist_geolocation` |
| `product_category_name_translation.csv` | `raw.product_category_name_translation` |

## Source Preservation

The original source columns must remain unchanged.

RAW ingestion should not:

- rename business columns;
- filter records;
- deduplicate records;
- impute missing values;
- apply KPI eligibility rules;
- reconcile monetary values;
- alter source identifiers.

## Ingestion Metadata

Additional technical metadata may be added without modifying the source values.

Planned metadata fields include:

- `_source_file_name`;
- `_source_row_number`;
- `_ingested_at`.

These fields support auditability and troubleshooting.

## Raw Data Types

CSV ingestion should favor source-safe loading.

Where practical, source fields should initially be loaded without applying analytical type assumptions.

Explicit business data types will be enforced in STAGING.

This reduces the risk of ingestion failures or silent type coercion.

---

# 5. RAW Ingestion Strategy

The source dataset is a static historical extract.

Therefore, the initial ingestion strategy will use:

> deterministic full reloads.

The ingestion pipeline must be idempotent.

Running the ingestion process repeatedly against the same source files should produce the same RAW database state.

Incremental ingestion is not required for v1 because no continuously changing source system is available.

If future incremental data becomes available, the ingestion strategy may be extended.

---

# 6. STAGING Schema

## Purpose

The `staging` schema standardizes RAW source data into analytically reliable typed relations.

STAGING remains close to the source and must not contain final business KPIs.

## Transformation Owner

> dbt.

## Default Materialization

> View.

Staging models are primarily lightweight transformations and therefore do not require independent physical storage in v1.

## Naming Convention

Staging models follow:

`stg_<source>__<entity>`

Examples:

- `stg_olist__customers`
- `stg_olist__orders`
- `stg_olist__order_items`
- `stg_olist__order_payments`
- `stg_olist__order_reviews`
- `stg_olist__products`
- `stg_olist__sellers`
- `stg_olist__geolocation`
- `stg_olist__category_translation`

## Responsibilities

STAGING may perform:

- column renaming;
- explicit data-type conversion;
- timestamp parsing;
- numeric casting;
- standardized null handling;
- standardized naming conventions;
- lightweight source-derived quality fields.

STAGING should not perform:

- KPI filtering;
- customer segmentation;
- RFM calculations;
- commercial population filtering;
- payment reconciliation;
- review consolidation;
- destructive anomaly removal.

Source-quality anomalies remain observable.

---

# 7. CORE Schema

## Purpose

The `core` schema implements the governed dimensional warehouse.

It contains reusable dimensions and atomic fact tables at validated business grains.

## Transformation Owner

> dbt.

## Default Materialization

> Table.

Core dimensions and facts are reusable warehouse structures and should therefore be physically persisted.

## Planned Dimensions

- `dim_customer`
- `dim_product`
- `dim_seller`
- `dim_geography`
- `dim_date`

## Planned Facts

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

## Core Modeling Rule

CORE must preserve validated grains.

Examples:

`fact_orders`
→ one row per `order_id`

`fact_order_items`
→ one row per `order_id + order_item_id`

`fact_payments`
→ one row per `order_id + payment_sequential`

`fact_reviews`
→ one row per `review_id + order_id`

Business processes with different grains must remain separate.

---

# 8. INTERMEDIATE Schema

## Purpose

The `intermediate` schema contains reusable transformations that:

- reconcile grains;
- aggregate atomic facts;
- apply governed analytical rules;
- prepare cross-domain integration;
- calculate reusable operational logic.

Intermediate models are not primarily designed for end-user consumption.

## Transformation Owner

> dbt.

## Naming Convention

Intermediate models use:

`int_<domain>_<purpose>`

or:

`int_order_<purpose>`

## Planned Models

### `int_order_commercial`

Grain:

> one row per `order_id`

Purpose:

Aggregate Order Items into governed order-level commercial measures.

---

### `int_order_payments`

Grain:

> one row per `order_id`

Purpose:

Aggregate payment records independently to order grain.

---

### `int_order_financial_reconciliation`

Grain:

> one row per comparable `order_id`

Purpose:

Compare independently aggregated commercial and payment measures using integer-cent arithmetic.

---

### `int_order_operations`

Grain:

> one row per `order_id`

Purpose:

Apply operational timestamp-quality rules and calculate governed delivery measures.

---

### `int_order_reviews`

Status:

> partially provisional.

Purpose:

Support controlled integration of reviews with order-level characteristics after the `POP-REV-02` review-consolidation decision is finalized.

---

# 9. Intermediate Materialization Strategy

Intermediate materialization will depend on reuse and transformation cost.

The default principle is:

> lightweight, single-use transformation → view

> computationally heavier or repeatedly reused transformation → table

Initial planned materializations are:

| Model | Planned Materialization |
|---|---|
| `int_order_commercial` | Table |
| `int_order_payments` | Table |
| `int_order_financial_reconciliation` | Table |
| `int_order_operations` | Table |
| `int_order_reviews` | View until modeling logic is finalized |

These choices may be reviewed after performance testing.

---

# 10. MARTS Schema

## Purpose

The `marts` schema contains business-facing analytical datasets.

These models translate governed warehouse logic into structures optimized for KPI calculation, dashboard consumption, and analytical use.

## Transformation Owner

> dbt.

## Default Materialization

> Table.

Marts are repeatedly queried by Tableau, SQL analysis, and Python workflows and should therefore be persisted.

## Planned Marts

- `mart_executive`
- `mart_commercial`
- `mart_customer`
- `mart_operations`
- `mart_customer_experience`

---

# 11. Analytical Access Pattern

The preferred downstream access path is:

CORE
↓
INTERMEDIATE
↓
MARTS
↓
Tableau / Python / Analytical SQL

Dashboards should primarily query:

> `marts`

rather than rebuilding business logic independently.

This prevents KPI definitions from being duplicated inside Tableau workbooks.

Python analyses may use marts or governed intermediate models depending on analytical requirements.

RAW should not be used directly for business reporting.

---

# 12. dbt Source Boundary

dbt will define the RAW tables as governed sources.

Conceptually:

source('olist', 'orders')

→ `raw.olist_orders`

source('olist', 'order_items')

→ `raw.olist_order_items`

and so forth.

Source definitions will support:

- source documentation;
- source-level tests;
- lineage;
- freshness metadata where appropriate in future implementations.

The static historical nature of the current dataset means real-time source freshness monitoring is not required for v1.

---

# 13. dbt Model Structure

The planned dbt project structure is:

dbt/
├── models/
│   ├── staging/
│   │   ├── olist/
│   │   │   ├── _olist__sources.yml
│   │   │   ├── _olist__models.yml
│   │   │   ├── stg_olist__customers.sql
│   │   │   ├── stg_olist__orders.sql
│   │   │   ├── stg_olist__order_items.sql
│   │   │   ├── stg_olist__order_payments.sql
│   │   │   ├── stg_olist__order_reviews.sql
│   │   │   ├── stg_olist__products.sql
│   │   │   ├── stg_olist__sellers.sql
│   │   │   ├── stg_olist__geolocation.sql
│   │   │   └── stg_olist__category_translation.sql
│   │
│   ├── core/
│   │   ├── dimensions/
│   │   └── facts/
│   │
│   ├── intermediate/
│   │
│   └── marts/
│       ├── executive/
│       ├── commercial/
│       ├── customer/
│       ├── operations/
│       └── customer_experience/
│
├── macros/
├── tests/
├── seeds/
└── snapshots/

Not every directory must immediately contain models.

The structure establishes the intended implementation boundaries.

---

# 14. PostgreSQL Schema Mapping

dbt models must resolve to the exact intended PostgreSQL schemas:

| dbt Layer | PostgreSQL Schema |
|---|---|
| Staging | `staging` |
| Core | `core` |
| Intermediate | `intermediate` |
| Marts | `marts` |

The RAW schema remains external to dbt model creation and is managed by ingestion.

Because dbt's default custom-schema behavior may prefix schema names with the target schema, the project will explicitly configure schema naming so physical schemas remain:

- `staging`
- `core`
- `intermediate`
- `marts`

rather than unintended names such as:

`analytics_staging`.

The exact dbt schema-generation configuration will be implemented during dbt project setup.

---

# 15. Naming Conventions

## RAW Tables

Source-oriented names:

`olist_orders`

`olist_order_items`

---

## STAGING

`stg_<source>__<entity>`

Example:

`stg_olist__orders`

---

## Dimensions

`dim_<entity>`

Example:

`dim_customer`

---

## Facts

`fact_<business_process>`

Example:

`fact_order_items`

---

## Intermediate Models

`int_<domain>_<purpose>`

Example:

`int_order_financial_reconciliation`

---

## Analytical Marts

`mart_<business_domain>`

Example:

`mart_commercial`

---

## Keys

Surrogate keys:

`<entity>_key`

Examples:

- `customer_key`
- `product_key`
- `seller_key`
- `geography_key`

Source identifiers retain their original semantic names.

---

## Boolean Flags

Boolean fields should use readable prefixes such as:

- `is_`
- `has_`

Examples:

- `is_completed_commercial_order`
- `is_late_delivery`
- `has_review`
- `has_valid_delivery_lead_time`

---

# 16. Transformation Ownership

Each layer has a strict transformation boundary.

| Logic | Layer |
|---|---|
| File loading | Python ingestion |
| Source preservation | RAW |
| Type conversion | STAGING |
| Source naming standardization | STAGING |
| Dimensional relationships | CORE |
| Surrogate keys | CORE |
| Data-quality eligibility flags | CORE / INTERMEDIATE |
| Atomic facts | CORE |
| Grain reconciliation | INTERMEDIATE |
| Payment reconciliation | INTERMEDIATE |
| Operational duration calculations | INTERMEDIATE |
| Customer lifecycle calculations | INTERMEDIATE / MARTS |
| KPI-ready metrics | MARTS |
| Visualization calculations | Minimal |

Business logic should be implemented as far upstream as appropriate without contaminating source-preservation layers.

---

# 17. Data Quality Strategy

Data-quality controls will exist across multiple layers.

## Ingestion

Validate:

- expected files;
- expected columns;
- source availability;
- row-load success.

## Staging

Validate:

- data types;
- accepted categorical values;
- required source keys;
- timestamp parsing.

## Core

Validate:

- unique dimension keys;
- unique fact grains;
- referential integrity;
- dimension relationships.

## Intermediate

Validate:

- aggregation grain;
- reconciliation rules;
- analytical-population eligibility;
- chronology-sensitive calculations.

## Marts

Validate:

- KPI consistency;
- expected population sizes;
- metric reconciliation;
- business-rule expectations.

---

# 18. Testing Strategy

dbt tests should include:

- `not_null`;
- `unique`;
- `relationships`;
- `accepted_values`;
- custom business-rule tests.

Examples include:

> `fact_orders.order_id` must be unique.

> `fact_order_items` must be unique by `order_id + order_item_id`.

> `fact_payments` must be unique by `order_id + payment_sequential`.

> `fact_reviews` must be unique by `review_id + order_id`.

Custom tests will also validate governed analytical assumptions such as:

- completed commercial eligibility;
- chronology-valid populations;
- payment reconciliation classifications;
- valid review-score range.

---

# 19. Reproducibility Strategy

A new environment should be able to reconstruct the analytical platform using:

1. repository source code;
2. original source CSV files;
3. Docker;
4. Python dependencies;
5. dbt dependencies;
6. documented execution commands.

The intended workflow is:

Start PostgreSQL
↓
Load RAW data
↓
Run dbt transformations
↓
Run dbt tests
↓
Generate analytical marts
↓
Connect analytics tools

No manually created production table should be required.

---

# 20. Environment Separation

The initial implementation is local development.

Future environments may include:

- development;
- CI testing;
- cloud deployment.

Environment-specific values such as:

- database host;
- port;
- username;
- password;
- database name;

must not be hard-coded into analytical SQL models.

Secrets must not be committed to GitHub.

Environment variables or ignored local configuration files will be used instead.

---

# 21. Physical Layer Summary

The resulting physical architecture is:

executive_commerce
│
├── raw
│   └── source-preserving PostgreSQL tables
│
├── staging
│   └── typed and standardized dbt views
│
├── core
│   ├── dimensions
│   └── atomic facts
│
├── intermediate
│   └── grain-reconciled and governed business logic
│
└── marts
    └── KPI-ready business-facing tables

Transformation ownership is:

Python
→ RAW

dbt
→ STAGING
→ CORE
→ INTERMEDIATE
→ MARTS

Downstream consumption is:

MARTS
→ SQL
→ Python
→ Tableau

---

# 22. Implementation Status

The physical architecture establishes:

- one PostgreSQL analytical database;
- five governed physical schemas;
- source-preserving RAW ingestion;
- clear Python/dbt ownership boundaries;
- dbt staging conventions;
- physical core dimensions and facts;
- intermediate grain-reconciliation models;
- persisted business marts;
- explicit model materialization strategy;
- schema naming conventions;
- test boundaries;
- data-quality responsibilities;
- reproducible local infrastructure;
- future environment portability.

The next implementation stage is:

> **M2 — PostgreSQL Docker Infrastructure**

This stage will create and validate the local PostgreSQL service that will host the warehouse.