# Executive Commerce Intelligence Platform — Data Model

## 1. Purpose

This document defines the logical dimensional model for the Executive Commerce Intelligence Platform.

The model translates validated business requirements, source-profiling evidence, analytical population rules, and governed KPI definitions into a warehouse structure designed for reliable analytical use.

The dimensional model supports:

* executive commercial reporting;
* customer lifecycle analytics;
* product and category performance;
* seller performance;
* logistics and delivery analysis;
* payment analytics;
* customer-experience analysis;
* reusable analytical marts;
* SQL and dbt transformations;
* Python analytical workflows;
* Tableau reporting.

The model prioritizes:

* explicit analytical grain;
* preservation of source lineage;
* protection against fanout;
* conformed dimensions;
* governed KPI populations;
* reproducible transformation logic.

---

# 2. Modeling Principles

## 2.1 Preserve Natural Business Grains

Each fact table represents one explicitly defined business-event grain.

The platform will not create a single universal transaction table because Orders, Order Items, Payments, and Reviews represent different business processes and have different natural grains.

Validated source grains are:

| Domain      | Validated Grain                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------- |
| Orders      | One row per `order_id`                                                                         |
| Order Items | One row per `order_id + order_item_id`                                                         |
| Payments    | One row per `order_id + payment_sequential`                                                    |
| Reviews     | One row per `review_id + order_id`                                                             |
| Customers   | One source row per `customer_id`, with persistent identity represented by `customer_unique_id` |
| Products    | One row per `product_id`                                                                       |
| Sellers     | One row per `seller_id`                                                                        |

Analytical transformations must preserve these grains unless an explicit downstream aggregation is being performed.

---

## 2.2 Separate Facts by Business Process

The warehouse will use independent fact tables for the major source business processes:

* `fact_orders`;
* `fact_order_items`;
* `fact_payments`;
* `fact_reviews`.

These facts must not be collapsed into a single atomic table.

This prevents multiplication of records when independent one-to-many relationships are combined.

---

## 2.3 Use Conformed Dimensions

Reusable descriptive entities will be modeled through conformed dimensions.

Planned conformed dimensions include:

* `dim_customer`;
* `dim_product`;
* `dim_seller`;
* `dim_date`;
* `dim_geography`.

The same dimension may play different analytical roles.

For example:

> `dim_geography`

can represent both customer transaction geography and seller geography through separate foreign keys in relevant facts.

---

## 2.4 Separate Source Identity from Warehouse Identity

Warehouse dimensions will use surrogate keys as analytical primary keys.

Source-system identifiers will remain preserved as natural business keys for:

* lineage;
* reconciliation;
* debugging;
* source traceability.

Example:

> `customer_key` → warehouse surrogate key

> `customer_unique_id` → persistent source business identifier

This allows the warehouse model to remain independent from the physical source-key implementation.

---

## 2.5 Preserve Source Anomalies

Source records must not be silently corrected or removed from raw, staging, or core warehouse layers solely because they fail a KPI-specific quality condition.

Instead, questionable source conditions should be represented through:

* explicit quality flags;
* eligibility flags;
* downstream governed analytical populations.

For example:

> a carrier-handoff timestamp occurring before approval remains preserved in the warehouse but is excluded from chronology-dependent duration metrics.

---

## 2.6 Avoid Analytical Fanout

The following source relationships are potentially one-to-many:

> Orders → Order Items

> Orders → Payments

> Orders → Reviews

Therefore, atomic facts must not be directly joined together for analytical aggregation without first establishing compatible grains.

Measures must be aggregated independently before cross-domain integration.

---

## 2.7 Preserve `order_id` as a Conformed Degenerate Identifier

All order-related facts preserve:

> `order_id`

as a shared business identifier.

`order_id` therefore acts as a conformed degenerate identifier across:

* `fact_orders`;
* `fact_order_items`;
* `fact_payments`;
* `fact_reviews`.

This allows lineage and controlled cross-domain reconciliation without requiring direct fact-to-fact foreign-key relationships.

Important:

> Sharing `order_id` does not make unrestricted atomic fact-to-fact joins analytically safe.

Cross-domain analytics must still aggregate facts to compatible grains before integration.

---

## 2.8 Selectively Inherit Conformed Dimension Context

A lower-grain fact may inherit conformed dimensional context from its parent business event when doing so supports standard dimensional analysis without changing the fact grain.

For example, `fact_order_items` inherits:

* persistent customer;
* customer transaction geography;
* purchase date;

from the corresponding order.

This intentional denormalization allows commercial analysis directly at order-item grain without requiring routine joins from `fact_order_items` back to `fact_orders`.

Inherited dimensional context must not be interpreted as a new business event.

---

# 3. High-Level Logical Model

The warehouse is conceptually organized around independent fact tables connected through conformed dimensions.

```text
                                  dim_date
                                     │
             ┌───────────────────────┼────────────────────────┐
             │                       │                        │
             ▼                       ▼                        ▼

        fact_orders           fact_order_items           fact_reviews
             │                       │                        │
             │                       ├──── dim_product        │
             │                       │                        │
             │                       ├──── dim_seller         │
             │                       │                        │
             │                       ├──── dim_customer       │
             │                       │                        │
             │                       ├──── dim_geography      │
             │                       │     customer role      │
             │                       │                        │
             │                       └──── dim_geography      │
             │                             seller role        │
             │                                                │
             ├──── dim_customer                              │
             │                                                │
             └──── dim_geography                              │
                  customer role                               │
                                                              │
                                                      review date roles


                             fact_payments
```

The four facts share `order_id` for source lineage and controlled reconciliation.

They do not form a physical fact hierarchy.

---

# 4. Dimension Tables

## 4.1 `dim_customer`

### Grain

> One row per persistent `customer_unique_id`.

### Purpose

Represent the persistent analytical customer identity across multiple marketplace orders.

### Key Design

| Column               | Role                            |
| -------------------- | ------------------------------- |
| `customer_key`       | Warehouse surrogate primary key |
| `customer_unique_id` | Persistent source natural key   |

### Modeling Rationale

Source profiling confirmed:

* 99,441 distinct `customer_id` values;
* 96,096 distinct `customer_unique_id` values;
* 2,997 persistent identifiers appear in multiple customer records;
* one persistent customer appears through as many as 17 source customer records.

Therefore:

> `customer_unique_id`

is the appropriate persistent customer identifier for customer lifecycle analytics.

The transactional source identifier:

> `customer_id`

does not define the grain of `dim_customer`.

It remains preserved in the order fact for source lineage.

### Dimensional Scope

`dim_customer` should remain intentionally narrow.

It should not permanently store behavioral measures such as:

* first purchase date;
* last purchase date;
* order count;
* customer GMV;
* recency;
* frequency;
* monetary value;
* RFM segment.

These values depend on analytical windows or derived behavior and belong in customer analytical models and marts.

### Geography Treatment

Customer geography is not treated as a permanent attribute of the persistent customer dimension.

Different source `customer_id` records belonging to the same persistent customer may potentially represent different transaction-observed locations.

Therefore:

> customer geography is associated with the business event through `customer_geography_key`.

For orders, this context is stored in `fact_orders`.

For order-item commercial analysis, the same order-observed geography is inherited into `fact_order_items`.

This preserves geographic context without incorrectly treating geography as an immutable persistent-customer attribute.

---

# 5. `dim_product`

### Grain

> One row per `product_id`.

### Purpose

Provide reusable product descriptive attributes for commercial and marketplace analysis.

### Key Design

| Column        | Role                            |
| ------------- | ------------------------------- |
| `product_key` | Warehouse surrogate primary key |
| `product_id`  | Source natural key              |

### Candidate Attributes

* `product_category_name`;
* standardized English product category;
* product name length;
* product description length;
* product photo count;
* product weight;
* product length;
* product height;
* product width;
* category missing flag;
* category translation available flag.

### Data Quality Treatment

Profiling identified:

* 610 products without a category;
* 2 products missing at least one physical attribute;
* 2 Portuguese product categories without English translation.

These records must remain represented.

Missing categories should receive a governed analytical label such as:

> `Unknown / Unclassified`

rather than being removed through inner joins or filtering.

---

# 6. `dim_seller`

### Grain

> One row per `seller_id`.

### Purpose

Represent the marketplace seller entity.

### Key Design

| Column       | Role                            |
| ------------ | ------------------------------- |
| `seller_key` | Warehouse surrogate primary key |
| `seller_id`  | Source natural key              |

### Candidate Source Attributes

* seller ZIP-code prefix;
* seller city;
* seller state.

These source fields are preserved for traceability.

Governed seller geography analysis should use:

> `seller_geography_key`

from `fact_order_items` referencing `dim_geography`.

This avoids snowflaking `dim_seller` into the geography dimension.

### Source Validation

Source profiling confirmed:

* 3,095 seller records;
* 3,095 unique seller identifiers;
* 100% referential coverage from Order Items to Sellers.

---

# 7. `dim_geography`

### Planned Grain

> One standardized row per ZIP-code prefix.

### Status

> Logical design defined; geographic standardization rule remains provisional.

### Purpose

Provide reusable geographic enrichment for:

* customer transaction geography;
* seller geography;
* commercial analysis;
* delivery analysis;
* marketplace segmentation.

### Source Constraint

Raw geolocation cannot be used directly as a warehouse dimension.

Profiling identified:

* 1,000,163 source geolocation rows;
* 19,015 distinct ZIP-code prefixes;
* 261,831 exact duplicate rows beyond the first occurrence;
* 17,972 ZIP prefixes represented by multiple rows;
* up to 1,146 source observations for one ZIP prefix.

Therefore:

> direct analytical joins from customer or seller records to raw geolocation by ZIP-code prefix are prohibited.

### Candidate Attributes

* `geography_key`;
* ZIP-code prefix;
* standardized city;
* standardized state;
* representative latitude;
* representative longitude;
* source-record count;
* coordinate-observation count;
* geography-quality flag.

### Role-Playing Usage

The same `dim_geography` will be used through different fact-level roles.

Examples:

```text
fact_orders.customer_geography_key
                │
                ▼
          dim_geography
```

```text
fact_order_items.customer_geography_key
                    │
                    ▼
              dim_geography
```

and:

```text
fact_order_items.seller_geography_key
                    │
                    ▼
              dim_geography
```

This keeps the warehouse close to a star-schema structure.

### Pending Implementation Decision

A deterministic consolidation rule must be selected before physical implementation.

Possible approaches include:

* median coordinates per ZIP prefix;
* centroid after exact-duplicate removal;
* another explicitly documented robust aggregation strategy.

The chosen rule must produce a single controlled geography record per ZIP prefix.

---

# 8. `dim_date`

### Grain

> One row per calendar date.

### Purpose

Provide consistent calendar attributes across analytical facts.

### Candidate Attributes

* `date_key`;
* calendar date;
* day;
* day of week;
* day name;
* ISO week;
* month;
* month name;
* quarter;
* year;
* year-month;
* weekend flag;
* month-start flag;
* month-end flag.

### Role-Playing Date Usage

The same date dimension will support multiple business-date roles.

For `fact_orders`:

* `purchase_date_key`;
* `approval_date_key`;
* `carrier_handoff_date_key`;
* `customer_delivery_date_key`;
* `estimated_delivery_date_key`.

For `fact_order_items`:

* `purchase_date_key`;
* `shipping_limit_date_key`.

For `fact_reviews`:

* `review_creation_date_key`;
* `review_answer_date_key`.

### Timestamp Preservation

The original timestamps must remain available in the relevant fact tables.

Date keys support calendar segmentation.

Raw timestamps support:

* elapsed-time calculations;
* sequence validation;
* operational-quality analysis.

### Calendar Coverage

The generated date spine must cover the minimum through maximum relevant calendar dates observed across all supported date roles, including:

* order lifecycle dates;
* estimated delivery dates;
* shipping-limit dates;
* review creation dates;
* review answer dates.

The calendar must therefore not be generated solely from purchase dates.

Missing lifecycle timestamps must not be converted into artificial calendar dates.

Where a business milestone is unavailable, the corresponding date key may remain null unless a separate governed unknown-date strategy is later required.

---

# 9. Fact Tables

## 9.1 `fact_orders`

### Grain

> One row per `order_id`.

### Fact Type

> Accumulating snapshot fact.

The order lifecycle is represented by one row containing milestone timestamps across the progression of the business process.

Typical milestones include:

```text
Purchase
   ↓
Approval
   ↓
Carrier Handoff
   ↓
Customer Delivery
```

Estimated delivery is also retained as an expected-service milestone.

This structure is appropriate because multiple operational stages describe the lifecycle of the same business order.

### Purpose

Represent the marketplace order lifecycle and provide the central order-level business-event context.

### Key Structure

Candidate conformed dimension keys include:

* `customer_key`;
* `customer_geography_key`;
* `purchase_date_key`;
* `approval_date_key`;
* `carrier_handoff_date_key`;
* `customer_delivery_date_key`;
* `estimated_delivery_date_key`.

The fact also preserves:

* `order_id` — conformed degenerate business identifier.

A separate surrogate `order_key` is not required solely for connecting the other fact tables.

### Source Transaction Identifier

`customer_id` remains preserved in the fact.

It provides source-level linkage to the transactional customer record used by the original Orders dataset.

Customer behavior should nevertheless use:

> `customer_key` → `dim_customer` → `customer_unique_id`.

### Source Attributes

* `order_id`;
* `customer_id`;
* `order_status`;
* `order_purchase_timestamp`;
* `order_approved_at`;
* `order_delivered_carrier_date`;
* `order_delivered_customer_date`;
* `order_estimated_delivery_date`.

### Data Quality and Eligibility Flags

Candidate flags include:

* `is_completed_commercial_order`;
* `is_delivered_order`;
* `has_order_items`;
* `has_payment`;
* `has_review`;
* `has_valid_delivery_lead_time`;
* `has_valid_delivery_estimate_comparison`;
* `is_late_delivery`;
* `is_valid_approval_to_carrier_sequence`;
* `is_valid_carrier_to_customer_sequence`.

These flags support governed analytical populations without physically removing source records.

### Operational Measures

Core `fact_orders` should primarily preserve:

* source timestamps;
* lifecycle status;
* source identifiers;
* dimensional keys;
* quality flags.

Derived duration measures should generally be calculated downstream rather than stored as permanent atomic fact measures.

Examples include:

* Delivery Lead Time;
* Days Early / Late;
* Approval-to-Carrier Time;
* Carrier-to-Customer Time.

These measures depend on governed analytical populations such as:

* `POP-DEL-02`;
* `POP-DEL-03`;
* `POP-DEL-04`.

Therefore, they belong primarily in:

> `int_order_operations`

and downstream analytical marts.

---

# 10. `fact_order_items`

### Grain

> One row per `order_id + order_item_id`.

### Fact Type

> Transaction fact.

### Purpose

Represent individual merchandise line items associated with marketplace orders.

### Key Structure

Candidate conformed dimension keys include:

* `customer_key`;
* `customer_geography_key`;
* `purchase_date_key`;
* `product_key`;
* `seller_key`;
* `seller_geography_key`;
* `shipping_limit_date_key`.

The customer, customer geography, and purchase-date keys are inherited from the corresponding order context during transformation.

Their presence at order-item grain is intentional and allows standard commercial analysis without requiring joins from `fact_order_items` back to `fact_orders`.

This denormalization does not change the validated fact grain:

> one row per `order_id + order_item_id`.

### Degenerate Business Identifiers

* `order_id`;
* `order_item_id`.

### Measures

* `price`;
* `freight_value`.

### Inherited Order Eligibility

`fact_order_items` should also expose:

* `is_completed_commercial_order`.

This flag is derived from the corresponding order status and allows:

> `POP-COM-01 — Completed Commercial Orders`

to be applied directly at order-item grain.

The flag is analytical context rather than an independent item-level business event.

### Operational Timestamp

The source field:

> `shipping_limit_date`

must remain represented.

Planned warehouse fields include:

* `shipping_limit_timestamp`;
* `shipping_limit_date_key`.

The timestamp is preserved for operational analysis and potential future fulfillment metrics.

### Commercial Rule

Core commercial KPIs should use only Order Items where:

> `is_completed_commercial_order = true`.

However, the fact itself must retain order-item records associated with all observed order statuses.

### Dimensional Analysis

Because order-level dimensional context is intentionally inherited into this fact, common analyses can be performed directly from `fact_order_items`, including:

* Category GMV by purchase month;
* Category GMV by customer geography;
* Seller GMV by customer geography;
* Items Sold by customer segment;
* freight analysis by product and seller;
* commercial mix by purchase period.

This avoids routine fact-to-fact joins for standard commercial reporting.

### Important Grain Rule

Item measures cannot be combined directly with payment or review measures at atomic grain.

Order-item measures must first be aggregated to a compatible grain when cross-domain analysis is required.

---

# 11. `fact_payments`

### Grain

> One row per `order_id + payment_sequential`.

### Fact Type

> Transaction fact.

### Purpose

Represent individual observed marketplace payment records.

### Degenerate Business Identifiers

* `order_id`;
* `payment_sequential`.

### Source Attributes

* `payment_type`;
* `payment_installments`.

### Measures

* `payment_value`.

### Payment-Type Modeling Decision

`payment_type` remains directly in the payment fact for v1.

A separate `dim_payment_type` will not be created because the current source contains a small categorical classification without additional descriptive attributes that would justify an independent dimension.

If future payment metadata introduces richer classification or hierarchy, this decision can be reassessed.

### Multiplicity

Profiling identified:

* 103,886 payment records;
* 99,440 distinct orders represented;
* 2,961 orders with multiple payment rows;
* up to 29 payment records for one order.

Therefore:

> payment values must be aggregated to order grain before being combined with order-level or item-level analytical measures.

### Monetary Semantics

The following measures remain conceptually distinct:

* GMV;
* Freight Value;
* Payment Value.

Payment reconciliation profiling found:

* 98,665 comparable orders;
* 98,089 exact reconciliations;
* 98,362 reconciliations within one cent;
* 303 orders differing by more than one cent.

Therefore:

> `payment_value` must not be treated as a substitute for GMV or item price plus freight.

Reconciliation exceptions must remain visible rather than being silently adjusted.

---

# 12. `fact_reviews`

### Grain

> One row per `review_id + order_id`.

### Fact Type

> Event fact.

### Purpose

Represent observed customer-review events.

### Degenerate Business Identifiers

* `review_id`;
* `order_id`.

### Date Keys

* `review_creation_date_key`;
* `review_answer_date_key`.

### Measure

* `review_score`.

### Degenerate Textual Attributes

The following source text may remain attached to the review event:

* review title;
* review message.

These are descriptive textual attributes rather than quantitative measures.

### Source Timestamps

* review creation timestamp;
* review answer timestamp.

These timestamps remain available in addition to their calendar date keys.

### Important Cardinality Rule

`review_id` alone is not unique.

Profiling confirmed:

* 99,224 review rows;
* 98,673 distinct reviewed orders;
* 789 review IDs represented by multiple source rows;
* `review_id + order_id` uniquely identifies source review rows;
* 547 orders have multiple reviews;
* up to 3 review records exist for one order.

Therefore:

> reviews remain at review grain in the core warehouse.

### Review KPIs

Review-grain KPIs can be calculated directly from this fact, including:

* Average Review Score;
* Low Review Rate;
* High Review Rate.

Order-integrated customer-experience measures remain dependent on the final:

> `POP-REV-02`

modeling decision.

---

# 13. Fact and Dimension Relationships

The major dimensional relationships are conceptually:

```text
dim_customer
     1
     │
     N
fact_orders
```

```text
dim_geography
     1
     │
     N
fact_orders
```

where geography represents the customer location observed for the transaction.

Order-item dimensional relationships include:

```text
dim_customer
     1
     │
     N
fact_order_items
```

```text
dim_product
     1
     │
     N
fact_order_items
```

```text
dim_seller
     1
     │
     N
fact_order_items
```

and two role-based uses of geography:

```text
dim_geography
     1
     │
     N
fact_order_items
```

for customer transaction geography, and:

```text
dim_geography
     1
     │
     N
fact_order_items
```

for seller geography.

Date relationships are role-playing relationships from multiple facts to the shared `dim_date`.

---

# 14. Relationships Across Facts

The order-related facts share:

> `order_id`

as a conformed degenerate business identifier.

Conceptually:

```text
                      order_id
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        ▼                ▼                 ▼

fact_order_items   fact_payments      fact_reviews
```

`fact_orders` also contains one row per `order_id`.

However:

> the dimensional design does not require fact-to-fact foreign-key relationships.

The facts represent independent analytical processes.

Cross-fact integration must occur through governed intermediate models after grain reconciliation.

---

# 15. Surrogate Key Strategy

Warehouse dimensions use generated surrogate keys.

| Dimension | Surrogate Key   | Natural Key                  |
| --------- | --------------- | ---------------------------- |
| Customer  | `customer_key`  | `customer_unique_id`         |
| Product   | `product_key`   | `product_id`                 |
| Seller    | `seller_key`    | `seller_id`                  |
| Geography | `geography_key` | standardized ZIP-code prefix |
| Date      | `date_key`      | calendar date                |

Source identifiers remain present alongside surrogate keys when required for lineage.

Fact tables do not require artificial surrogate keys when their validated business grain already provides a reliable source identifier.

---

# 16. Slowly Changing Dimension Strategy

The source dataset is a historical extract rather than an incremental operational source containing reliable effective-dated dimension history.

Therefore, the v1 warehouse will use:

> deterministic snapshot-style dimensions.

Where standardization changes are made, current warehouse attributes may follow Type 1-style replacement behavior.

However:

> SCD Type 2 history will not be artificially generated where the source does not provide reliable historical attribute-change events.

Historical context that is explicitly observable in the source should instead remain attached to fact events.

A key example is customer transaction geography.

If future incremental source data becomes available, the SCD strategy should be reassessed.

---

# 17. Fanout Protection

The following atomic joins are unsafe:

```text
Order Items × Payments

Order Items × Reviews

Payments × Reviews
```

For example, an order containing:

```text
3 order items
2 payment records
2 review records
```

would generate:

```text
3 × 2 × 2 = 12 rows
```

if all three atomic facts were directly joined.

This would duplicate:

* GMV;
* freight;
* payment values;
* review observations.

Therefore:

> atomic fact tables must never be combined directly for additive analytical measures without prior aggregation.

---

# 18. Intermediate Order-Level Integration

Cross-domain analysis will use reusable intermediate models.

## 18.1 `int_order_commercial`

### Purpose

> Aggregate merchandise and freight information from `fact_order_items` to order grain.

### Grain

> One row per `order_id`.

### Potential Fields

* `order_id`;
* order GMV;
* total freight;
* item count;
* distinct seller count;
* distinct product count;
* distinct category count;
* completed-commercial-order indicator.

This model provides a controlled order-grain commercial representation.

---

## 18.2 `int_order_payments`

### Purpose

> Aggregate `fact_payments` to order grain.

### Grain

> One row per `order_id`.

### Potential Fields

* `order_id`;
* total payment value;
* payment record count;
* payment-type count;
* maximum installment count.

This model represents payment information independently from commercial merchandise measures.

Payment reconciliation does not belong exclusively to this model because reconciliation requires information from both payment and commercial domains.

---

## 18.3 `int_order_financial_reconciliation`

### Purpose

> Compare independently aggregated commercial and payment measures at a compatible one-row-per-order grain.

### Grain

> One row per comparable `order_id`.

### Inputs

* `int_order_commercial`;
* `int_order_payments`.

### Potential Fields

* `order_id`;
* item value in integer cents;
* freight value in integer cents;
* total item-plus-freight value in integer cents;
* total payment value in integer cents;
* reconciliation difference in integer cents;
* exact-reconciliation flag;
* within-one-cent reconciliation flag;
* material reconciliation-exception flag.

### Important Rule

Reconciliation calculations must use:

> integer-cent arithmetic

rather than floating-point equality.

The model must preserve the distinction:

> GMV ≠ Payment Value ≠ Freight Value

as separate governed monetary concepts.

This intermediate model is intended for:

* reconciliation;
* data-quality investigation;
* auditability;
* exception monitoring.

It must not redefine the underlying commercial measures.

Conceptually:

```text
fact_order_items
      │
      ▼
int_order_commercial ─────────┐
                              │
                              ▼
              int_order_financial_reconciliation
                              ▲
                              │
int_order_payments ───────────┘
      ▲
      │
fact_payments
```

---

## 18.4 `int_order_operations`

### Purpose

> Apply governed operational-quality rules and derive order-level logistics measures.

### Grain

> One row per relevant `order_id`.

### Potential Measures

* Delivery Lead Time;
* Days Early / Late;
* Approval-to-Carrier Time;
* Carrier-to-Customer Time.

### Potential Flags

* late delivery;
* valid delivery lead time;
* valid delivery-estimate comparison;
* valid approval-to-carrier sequence;
* valid carrier-to-customer sequence.

### Population Alignment

This model supports:

* `POP-DEL-02`;
* `POP-DEL-03`;
* `POP-DEL-04`.

Chronology-sensitive measures must only be calculated where their required timestamp sequence is valid.

Source anomalies remain preserved upstream.

---

## 18.5 `int_order_reviews`

### Status

> Partially provisional.

### Purpose

> Support controlled integration between review outcomes and order-level characteristics.

The final aggregation strategy depends on:

> `POP-REV-02 — Order-Integrated Review Population`.

Possible strategies include:

* retaining review grain;
* selecting a canonical review;
* explicitly aggregating multiple reviews to one order-level outcome.

Until this decision is finalized, no arbitrary one-review-per-order assumption should be introduced.

---

# 19. Core-to-Mart Architecture

The logical flow is:

```text
RAW SOURCE DATA
      ↓
STAGING
      ↓
CORE DIMENSIONS + FACTS
      ↓
INTERMEDIATE DOMAIN MODELS
      ↓
ANALYTICAL MARTS
      ↓
KPIs / Tableau / Python
```

The layers have distinct responsibilities.

### Raw

Preserve source files unchanged.

### Staging

Standardize:

* names;
* data types;
* timestamps;
* categorical values;
* source-level quality fields.

### Core Warehouse

Represent:

* governed business grains;
* conformed dimensions;
* reusable analytical relationships;
* source identifiers;
* quality and eligibility context.

### Intermediate

Perform:

* grain reconciliation;
* cross-domain aggregation;
* reusable business calculations;
* financial reconciliation;
* operational eligibility logic.

### Marts

Provide KPI-ready analytical datasets aligned with business questions.

---

# 20. Fact-to-Mart Mapping

| Core Domain                            | Primary Analytical Marts                                                         |
| -------------------------------------- | -------------------------------------------------------------------------------- |
| `fact_orders`                          | `mart_executive`, `mart_customer`, `mart_operations`, `mart_customer_experience` |
| `fact_order_items`                     | `mart_executive`, `mart_commercial`, `mart_customer`                             |
| `fact_payments`                        | payment analytics and selected order-level marts after aggregation               |
| `fact_reviews`                         | `mart_customer_experience`                                                       |
| Customer lifecycle intermediate models | `mart_customer`, `mart_executive`                                                |
| Geographic enrichment                  | commercial, customer, seller, and operational marts                              |
| `int_order_financial_reconciliation`   | data-quality and reconciliation analysis                                         |

---

# 21. Planned Analytical Marts

## 21.1 `mart_executive`

### Purpose

Provide an executive-level view of marketplace performance.

### Expected Content

* GMV;
* Completed Commercial Orders;
* AOV;
* Active Customers;
* New Customers;
* Repeat Customers;
* commercial growth metrics;
* delivery indicators;
* review summary indicators.

Measures must use their governed analytical populations.

---

## 21.2 `mart_commercial`

### Purpose

Support product, category, seller, and marketplace performance analysis.

### Expected Content

* Category GMV;
* Category GMV Share;
* Seller GMV;
* Seller Order Volume;
* Seller Customer Count;
* Items Sold;
* freight-related commercial measures;
* commercial mix metrics.

The inherited conformed dimensional context in `fact_order_items` allows standard commercial breakdowns without routine fact-to-fact joins.

---

## 21.3 `mart_customer`

### Purpose

Support persistent customer lifecycle and value analysis.

### Expected Content

* Active Customers;
* New Customers;
* Repeat Customers;
* Repeat Purchase Rate;
* Orders per Customer;
* Customer GMV;
* acquisition cohort;
* cohort retention;
* Recency;
* Frequency;
* Monetary Value;
* RFM segmentation.

Behavioral attributes belong here rather than permanently inside `dim_customer`.

---

## 21.4 `mart_operations`

### Purpose

Support fulfillment and logistics performance analysis.

### Expected Content

* Delivery Lead Time;
* Days Early / Late;
* Late Delivery Rate;
* Carrier Handoff Time;
* Carrier Delivery Time;
* Average Freight per Order;
* Freight-to-GMV Ratio;
* operational sequence-quality indicators.

All chronology-sensitive metrics must follow their governed eligibility populations.

---

## 21.5 `mart_customer_experience`

### Purpose

Support customer review and delivery-experience analysis.

### Expected Content

* Average Review Score;
* Low Review Rate;
* High Review Rate;
* review-score distribution;
* delivery-review associations.

Order-integrated review metrics must not be implemented until the review-to-order consolidation strategy is finalized.

---

# 22. KPI Population Mapping

The dimensional and intermediate models must support the governed analytical populations defined in the KPI Framework.

| Population    | Primary Model Support                                                                |
| ------------- | ------------------------------------------------------------------------------------ |
| `POP-ORD-01`  | `fact_orders`                                                                        |
| `POP-COM-01`  | `fact_orders`, `fact_order_items`, `int_order_commercial`                            |
| `POP-CUST-01` | `dim_customer` + completed commercial order context                                  |
| `POP-DEL-01`  | `fact_orders`                                                                        |
| `POP-DEL-02`  | `int_order_operations`                                                               |
| `POP-DEL-03`  | `int_order_operations`                                                               |
| `POP-DEL-04`  | `int_order_operations`                                                               |
| `POP-PAY-01`  | `fact_payments`                                                                      |
| `POP-PAY-02`  | `int_order_commercial` + `int_order_payments` + `int_order_financial_reconciliation` |
| `POP-REV-01`  | `fact_reviews`                                                                       |
| `POP-REV-02`  | provisional `int_order_reviews` logic                                                |
| `POP-GEO-01`  | `dim_geography` after standardization                                                |
| `POP-TIME-01` | `dim_date` + calendar-period governance                                              |

---

# 23. Data Quality Integration

Data-quality results from profiling should remain observable downstream.

## 23.1 Order Quality

Examples include:

* missing lifecycle timestamps;
* invalid temporal sequences;
* orders without items;
* orders without payments;
* orders without reviews.

Relevant context should be exposed through `fact_orders` and `int_order_operations`.

---

## 23.2 Product Quality

Examples include:

* missing categories;
* missing physical attributes;
* missing category translations.

These conditions must remain visible in `dim_product`.

---

## 23.3 Payment Quality

Examples include:

* payment multiplicity;
* zero payment values;
* reconciliation differences.

Cross-domain reconciliation belongs in:

> `int_order_financial_reconciliation`.

---

## 23.4 Geography Quality

Examples include:

* source duplication;
* multiple coordinate observations per ZIP prefix;
* inconsistent representations;
* geography consolidation quality.

These conditions must be addressed deterministically before `dim_geography` is considered implementation-ready.

---

## 23.5 Review Quality

Examples include:

* multiple reviews per order;
* repeated `review_id` values;
* orders without reviews.

Missing reviews must remain conceptually distinct from low review scores.

---

# 24. Open Modeling Decisions

The following decisions intentionally remain unresolved.

## 24.1 Geographic Standardization

A deterministic consolidation method must be selected for:

> `dim_geography`.

The final decision must produce one governed representation per ZIP-code prefix.

---

## 24.2 Comparable Time Periods

`POP-TIME-01` must be finalized before implementing:

* GMV Growth Rate;
* Orders Growth Rate.

Boundary periods must not automatically be treated as complete calendar periods.

---

## 24.3 RFM Reference Date

A governed reference date must be selected before implementing:

> Customer Recency.

The reference date must be reproducible and explicitly documented.

---

## 24.4 Review-to-Order Consolidation

A rule for orders containing multiple review records must be finalized before implementing order-integrated review KPIs.

Potential strategies include:

* review-grain analysis;
* canonical review selection;
* explicit order-level aggregation.

No arbitrary consolidation rule will be introduced before this decision is supported by further source investigation.

---

# 25. Logical Model Status

The current logical model establishes:

* validated atomic fact grains;
* persistent customer identity;
* independent order, item, payment, and review facts;
* conformed dimensions;
* shared degenerate `order_id`;
* surrogate dimension-key strategy;
* role-playing date usage;
* complete calendar-spine coverage rules;
* role-playing geography usage;
* transaction-observed customer geography;
* inherited customer and purchase context at order-item grain;
* seller geography at order-item fact context;
* accumulating-snapshot treatment of Orders;
* transaction-fact treatment of Order Items and Payments;
* event-fact treatment of Reviews;
* preservation of `shipping_limit_date`;
* payment-type treatment without unnecessary dimension creation;
* explicit fanout-protection rules;
* quality and eligibility flag strategy;
* intermediate grain-reconciliation models;
* separate cross-domain financial reconciliation;
* integer-cent reconciliation logic;
* KPI-aligned analytical marts;
* deterministic snapshot-style dimension strategy.

The logical architecture is therefore:

```text
RAW
 │
 ▼
STAGING
 │
 ▼
CORE
 ├── Dimensions
 └── Atomic Facts
        │
        ▼
INTERMEDIATE
 ├── int_order_commercial
 ├── int_order_payments
 ├── int_order_financial_reconciliation
 ├── int_order_operations
 └── int_order_reviews
        │
        ▼
MARTS
 ├── mart_executive
 ├── mart_commercial
 ├── mart_customer
 ├── mart_operations
 └── mart_customer_experience
        │
        ▼
ANALYTICS
 ├── SQL
 ├── Python
 └── Tableau
```

The next stage will translate this logical design into:

> physical PostgreSQL schemas and dbt models.

Physical implementation must preserve the grains, dimensional relationships, eligibility logic, fanout controls, and governance principles documented here rather than reintroducing source-level denormalized joins.
