# KPI Framework

## Executive Commerce Intelligence Platform

### 1. Purpose

This document defines the governed business metrics used by the Executive Commerce Intelligence Platform.

The KPI framework establishes consistent definitions, calculation rules, analytical grain, populations, ownership, and traceability so that equivalent metrics produce consistent results across:

* analytical data marts;
* SQL analyses;
* Python analyses;
* statistical analyses;
* executive dashboards;
* portfolio documentation.

KPI definitions may be refined after source-data profiling when empirical characteristics of the dataset require additional rules.

Material definition changes must be documented and version-controlled.

---

### 2. KPI Governance Principles

#### 2.1 Explicit Business Definition

Every KPI must have a clear business interpretation independent of its technical implementation.

A metric should answer:

> **What business concept is this number intended to represent?**

---

#### 2.2 Explicit Grain

Every KPI must identify its natural analytical grain.

Examples include:

* order;
* order item;
* customer;
* seller;
* payment;
* review;
* calendar period;
* geographic segment.

Measures originating at different grains must not be combined without validation against duplication or aggregation errors.

---

#### 2.3 Explicit Analytical Population

Each KPI must define which records are eligible for inclusion.

Where relevant, this includes:

* order status;
* date range;
* required timestamps;
* missing-value rules;
* valid identifiers;
* minimum-volume thresholds.

There will be no undocumented global filter applied to all metrics.

---

#### 2.4 Governed Core Metrics

Business-critical metrics should be calculated in governed analytical layers whenever practical rather than independently recreated in dashboards or notebooks.

Preferred flow:

> **Source → dbt / SQL Transformation → Analytical Mart → Dashboard / Analysis**

---

#### 2.5 No Unsupported Financial Interpretation

Marketplace transaction values will not automatically be interpreted as accounting revenue, net revenue, contribution margin, or profit.

Where appropriate, the project will use **Gross Merchandise Value (GMV)** to represent merchandise transaction value supported by the available data.

---

#### 2.6 First Observed Customer Activity

Because the dataset represents a finite historical observation window, customer lifecycle metrics must distinguish between:

* **first observed purchase**, and
* true lifetime first purchase.

The project cannot prove customer behavior outside the observation window.

---

#### 2.7 Metric Status

Each KPI will have one of the following statuses:

| Status          | Meaning                                                                    |
| --------------- | -------------------------------------------------------------------------- |
| **Provisional** | Initial definition subject to confirmation during data profiling           |
| **Validated**   | Definition confirmed against source-data behavior and project requirements |
| **Revised**     | Definition materially changed after validation, with rationale documented  |

All KPIs are considered **Provisional** until source-data profiling is completed.

---

### 3. KPI Definition Template

Each governed KPI should document:

| Attribute                   | Description                               |
| --------------------------- | ----------------------------------------- |
| **KPI ID**                  | Unique metric identifier                  |
| **Name**                    | Business-facing metric name               |
| **Definition**              | Business meaning                          |
| **Formula**                 | Calculation logic                         |
| **Natural Grain**           | Lowest relevant level of calculation      |
| **Analytical Population**   | Eligible records                          |
| **Primary Dimensions**      | Dimensions used for analysis              |
| **Expected Source / Model** | Planned analytical source                 |
| **Business Owner**          | Primary stakeholder                       |
| **Supports**                | Related business questions / requirements |
| **Status**                  | Provisional, Validated, or Revised        |

---

# 4. Executive & Commercial KPIs

## KPI-001 — Gross Merchandise Value (GMV)

**Status:** Validated

**Business Definition:**
Total merchandise transaction value represented by the price of eligible order items associated with completed commercial orders during the analytical period.

**Formula:**

> **GMV = SUM(order item price)**

**Natural Grain:**
Order item

**Analytical Population:**
POP-COM-01 — Completed Commercial Orders

Only order items associated with orders where:

order_status = 'delivered'

are included in the core commercial GMV population.

**Excludes by Default:**

* freight value;
* payment value;
* accounting adjustments unavailable in the dataset.

**Primary Dimensions:**

* date;
* product category;
* seller;
* customer geography;
* seller geography.

**Expected Source / Model:**
`fact_order_items` → `mart_executive`, `mart_commercial`

**Business Owner:**
Executive Management / Commercial Management

**Supports:**
BQ-01, BQ-02, BQ-05, BQ-06
BR-001, BR-002, BR-005, BR-006

---

## KPI-002 — Completed Commercial Orders

**Status:** Revised

**Business Definition:**
Number of distinct marketplace orders representing completed commercial transactions.

**Formula:**

> **Completed Commercial Orders = COUNT(DISTINCT order_id)**

**Natural Grain:**
Order

**Analytical Population:**
POP-COM-01 — Completed Commercial Orders

Eligibility requires:

order_status = 'delivered'

Source profiling confirmed that all delivered orders contain corresponding order-item records.

**Important Rule:**
This KPI replaces the original generic Valid Orders definition for core commercial reporting.

The complete observed order population, including non-delivered statuses, remains available separately through POP-ORD-01.

**Primary Dimensions:**

* purchase date;
* customer geography;
* product category;
* seller.

**Expected Source / Model:**
`fact_orders` → `mart_executive`, `mart_commercial`

**Business Owner:**
Executive Management

**Supports:**
BQ-01, BQ-02, BQ-03, BQ-05
BR-001, BR-002, BR-003, BR-005

---

## KPI-003 — Average Order Value (AOV)

**Status:** Validated

**Business Definition:**
Average merchandise transaction value generated by a completed commercial order.

**Formula:**

> **AOV = GMV / Completed Commercial Orders**

**Natural Grain:**
Order after item-level GMV has been aggregated to order level.

**Important Rule:**
AOV must not be calculated as the average order-item price.

**Analytical Population:**
POP-COM-01 — Completed Commercial Orders

The GMV numerator and completed-order denominator must represent the same governed commercial population.

**Primary Dimensions:**

* month;
* customer geography;
* product category;
* seller;
* customer segment.

**Expected Source / Model:**
`fact_orders` / aggregated `fact_order_items` → `mart_executive`

**Business Owner:**
Executive Management / Finance

**Supports:**
BQ-01, BQ-02, BQ-05
BR-001, BR-002, BR-005

---

## KPI-004 — GMV Growth Rate

**Status:** Provisional

**Business Definition:**
Percentage change in GMV between comparable analytical periods.

**Formula:**

> **GMV Growth = (Current Period GMV − Previous Comparable Period GMV) / Previous Comparable Period GMV**

**Natural Grain:**
Calendar period

**Comparison Types:**

* Month-over-Month (MoM);
* Year-over-Year (YoY), where sufficiently complete comparable periods exist.

**Analytical Population:**
Periods with adequate and comparable source-data coverage.

Incomplete observation periods must not be interpreted as normal growth periods.

**Expected Source / Model:**
`mart_executive`

**Business Owner:**
Executive Management

**Supports:**
BQ-01, BQ-02
BR-001, BR-002

---

## KPI-005 — Orders Growth Rate

**Status:** Provisional

**Business Definition:**
Percentage change in completed commercial orders between comparable analytical periods.

**Formula:**

> **Orders Growth = (Current Period Completed Commercial Orders − Previous Comparable Period Completed Commercial Orders) / Previous Comparable Period Completed Commercial Orders**

**Natural Grain:**
Calendar period

**Expected Source / Model:**
`mart_executive`

**Business Owner:**
Executive Management

**Supports:**
BQ-01, BQ-02
BR-001, BR-002

---

# 5. Customer KPIs

## KPI-006 — Active Customers

**Status:** Validated

**Business Definition:**
Number of distinct persistent customers with at least one valid purchase during the analytical period.

**Formula:**

> **Active Customers = COUNT(DISTINCT customer_unique_id)**

**Natural Grain:**
Persistent customer

**Important Rule:**
`customer_unique_id` must be used rather than transaction-specific `customer_id` when identifying customers across orders.

**Analytical Population:**
Persistent customers associated with at least one valid order during the selected period.

**Primary Dimensions:**

* period;
* acquisition cohort;
* geography;
* customer segment.

**Expected Source / Model:**
`dim_customer` + `fact_orders` → `mart_customer`, `mart_executive`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-01, BQ-02, BQ-03, BQ-04
BR-001, BR-003, BR-004

---

## KPI-007 — New Customers

**Status:** Validated

**Business Definition:**
Number of customers whose first **observed valid purchase** occurs within the analytical period.

**Formula:**

For each persistent customer:

> **First Observed Purchase = MIN(valid purchase timestamp)**

Then:

> **New Customers = customers whose First Observed Purchase falls within the selected period**

**Natural Grain:**
Persistent customer

**Important Limitation:**
The dataset does not establish whether the customer's first observed purchase is their true lifetime first purchase.

**Expected Source / Model:**
`dim_customer` / customer lifecycle model → `mart_customer`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-01, BQ-03
BR-002, BR-003

---

## KPI-008 — Repeat Customers

**Status:** Validated

**Business Definition:**
Customers with more than one observed valid marketplace order.

**Formula:**

> **Repeat Customer = customer with COUNT(DISTINCT valid order_id) > 1**

**Natural Grain:**
Persistent customer

**Expected Source / Model:**
Customer lifecycle model → `mart_customer`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-03
BR-003

---

## KPI-009 — Repeat Purchase Rate

**Status:** Validated

**Business Definition:**
Share of observed customers who completed more than one valid marketplace order during the available observation window.

**Default Formula:**

> **Repeat Purchase Rate = Repeat Customers / Customers with at least one valid order**

**Natural Grain:**
Persistent customer

**Important Limitation:**
This metric is affected by observation-window length. Customers acquired near the end of the dataset have less opportunity to make a repeat purchase.

Cohort-based analysis should therefore accompany the aggregate metric.

**Expected Source / Model:**
`mart_customer`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-02, BQ-03
BR-003

---

## KPI-010 — Orders per Customer

**Status:** Validated

**Business Definition:**
Average number of valid marketplace orders associated with an active customer.

**Formula:**

> **Orders per Customer = Completed Commercial Orders / Active Customers**

**Natural Grain:**
Customer population / analytical period

**Expected Source / Model:**
`mart_customer`, `mart_executive`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-01, BQ-03, BQ-04

---

## KPI-011 — Customer GMV

**Status:** Validated

**Business Definition:**
Cumulative GMV associated with a persistent customer within the analytical observation period.

**Formula:**

> **Customer GMV = SUM(GMV associated with customer's valid orders)**

**Natural Grain:**
Persistent customer

**Important Interpretation:**
Customer GMV represents observed marketplace transaction value and should not be described as profit or true lifetime value.

**Expected Source / Model:**
Customer-level analytical model → `mart_customer`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-04
BR-004

---

## KPI-012 — Cohort Retention Rate

**Status:** Validated

**Business Definition:**
Percentage of customers from an acquisition cohort who make another valid purchase in a subsequent cohort period.

For acquisition cohort (c) and relative period (t):

> **Cohort Retention(c,t) = Active Customers from Cohort c in Period t / Original Customers in Cohort c**

**Natural Grain:**
Acquisition cohort × relative period

**Acquisition Cohort:**
Month of first observed valid purchase.

**Important Limitation:**
Later cohorts have shorter observable retention horizons.

**Expected Source / Model:**
Customer cohort model → `mart_customer`

**Business Owner:**
Customer / Growth Team

**Supports:**
BQ-03
BR-003

---

## KPI-013 — Customer Recency

**Status:** Provisional

**Business Definition:**
Number of days between a customer's most recent observed valid purchase and the analytical reference date.

**Formula:**

> **Recency = Reference Date − Most Recent Valid Purchase Date**

**Natural Grain:**
Persistent customer

**Use:**
RFM segmentation.

**Expected Source / Model:**
Customer RFM model → `mart_customer`

**Supports:**
BQ-04
BR-004

---

## KPI-014 — Customer Frequency

**Status:** Validated

**Business Definition:**
Number of distinct valid orders associated with a persistent customer during the observation window.

**Formula:**

> **Frequency = COUNT(DISTINCT valid order_id)**

**Natural Grain:**
Persistent customer

**Use:**
RFM segmentation.

**Expected Source / Model:**
Customer RFM model → `mart_customer`

**Supports:**
BQ-04
BR-004

---

## KPI-015 — Customer Monetary Value

**Status:** Validated

**Business Definition:**
Observed cumulative GMV associated with a persistent customer.

**Formula:**

> **Monetary Value = SUM(customer GMV)**

**Natural Grain:**
Persistent customer

**Use:**
RFM segmentation.

**Important Interpretation:**
This is an observed transaction-value measure and is not equivalent to predictive Customer Lifetime Value.

**Expected Source / Model:**
Customer RFM model → `mart_customer`

**Supports:**
BQ-04
BR-004

# 6. Commercial & Marketplace KPIs

## KPI-016 — Items Sold

**Status:** Validated

**Business Definition:**
Number of order-item records associated with completed commercial orders.

**Formula:**

> **Items Sold = COUNT(order-item records)**

Where `order_item_id` represents the sequence of an item within an order, each valid order-item record is treated as one sold item unless profiling identifies a different interpretation.

**Natural Grain:**
Order item

**Validated Source Grain:**
order_id + order_item_id

uniquely identifies the 112,650 observed source order-item records.

**Analytical Population:**
POP-COM-01 — Completed Commercial Orders

**Primary Dimensions:**

* product category;
* seller;
* purchase period;
* customer geography.

**Expected Source / Model:**
`fact_order_items` → `mart_commercial`

**Business Owner:**
Commercial / Marketplace Management

**Supports:**
BQ-05, BQ-06
BR-005, BR-006

---

## KPI-017 — Category GMV

**Status:** Validated

**Business Definition:**
Total GMV associated with a standardized product category.

**Formula:**

> **Category GMV = SUM(eligible order-item price)**

grouped by standardized product category.

**Natural Grain:**
Product category × analytical period

**Important Rule:**
Categories with missing or unavailable classifications must remain identifiable rather than being silently removed.

**Expected Source / Model:**
`fact_order_items` + `dim_product` → `mart_commercial`

**Business Owner:**
Commercial / Marketplace Management

**Supports:**
BQ-05, BQ-06
BR-005

---

## KPI-018 — Category GMV Share

**Status:** Validated

**Business Definition:**
Share of marketplace GMV generated by a product category during the analytical period.

**Formula:**

> **Category GMV Share = Category GMV / Total GMV**

**Natural Grain:**
Product category × analytical period

**Use:**
Commercial mix and concentration analysis.

**Expected Source / Model:**
`mart_commercial`

**Business Owner:**
Commercial / Marketplace Management

**Supports:**
BQ-01, BQ-05

---

## KPI-019 — Seller GMV

**Status:** Validated

**Business Definition:**
Total GMV associated with eligible order items sold by a marketplace seller.

**Formula:**

> **Seller GMV = SUM(eligible order-item price)**

**Natural Grain:**
Seller

**Primary Dimensions:**

* analytical period;
* seller geography;
* product category.

**Expected Source / Model:**
`fact_order_items` + `dim_seller` → `mart_commercial`

**Business Owner:**
Commercial / Marketplace Management

**Supports:**
BQ-05, BQ-06
BR-006

---

## KPI-020 — Seller Order Volume

**Status:** Validated

**Business Definition:**
Number of distinct valid orders containing at least one item associated with a seller.

**Formula:**

> **Seller Order Volume = COUNT(DISTINCT order_id)**

grouped by seller.

**Natural Grain:**
Seller

**Important Rule:**
An order containing items from multiple sellers may legitimately contribute one order to each relevant seller's order count.

This metric should not therefore be summed across sellers to calculate marketplace total orders.

**Expected Source / Model:**
`fact_order_items` → `mart_commercial`

**Business Owner:**
Commercial / Marketplace Management

**Supports:**
BQ-05, BQ-06
BR-006

---

## KPI-021 — Seller Customer Count

**Status:** Validated

**Business Definition:**
Number of distinct persistent customers associated with valid orders containing items sold by a seller.

**Formula:**

> **Seller Customer Count = COUNT(DISTINCT customer_unique_id)**

grouped by seller.

**Natural Grain:**
Seller

**Expected Source / Model:**
`fact_order_items` + `fact_orders` + `dim_customer` → `mart_commercial`

**Business Owner:**
Commercial / Marketplace Management

**Supports:**
BQ-05
BR-006

---

# 7. Logistics & Operations KPIs

## KPI-022 — Delivery Lead Time

**Status:** Validated

**Business Definition:**
Elapsed time between customer purchase and confirmed delivery to the customer.

**Formula:**

> **Delivery Lead Time = Actual Customer Delivery Timestamp − Purchase Timestamp**

**Natural Grain:**
Order

**Default Unit:**
Days

**Analytical Population:**
Delivered orders containing valid purchase and customer-delivery timestamps.

**Primary Dimensions:**

* purchase period;
* customer state;
* seller;
* product category.

**Expected Source / Model:**
`fact_orders` → `mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-07, BQ-09
BR-008, BR-011

---

## KPI-023 — Days Early / Late

**Status:** Validated

**Business Definition:**
Difference between actual customer delivery and the estimated delivery date.

**Formula:**

> **Days Early/Late = Actual Delivery Date − Estimated Delivery Date**

Interpretation:

* negative value → delivered early;
* zero → delivered on estimated date;
* positive value → delivered late.

**Natural Grain:**
Order

**Analytical Population:**
Delivered orders with valid actual and estimated delivery timestamps.

**Expected Source / Model:**
`fact_orders` → `mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-07, BQ-08, BQ-09

---

## KPI-024 — Late Delivery Rate

**Status:** Validated

**Business Definition:**
Proportion of comparable delivered orders whose actual delivery occurred after the estimated delivery date.

**Formula:**

> **Late Delivery Rate = Late Delivered Orders / Delivered Orders with Valid Actual and Estimated Delivery Dates**

**Natural Grain:**
Order population

**Important Rule:**
Orders missing either timestamp must not be included automatically in the denominator.

**Primary Dimensions:**

* period;
* state;
* seller;
* category.

**Expected Source / Model:**
`mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-02, BQ-06, BQ-07, BQ-08, BQ-09
BR-008, BR-009, BR-011

---

## KPI-025 — Average Freight Value per Order

**Status:** Validated

**Business Definition:**
Average freight value associated with a valid marketplace order.

**Formula:**

First aggregate freight to order grain:

> **Order Freight = SUM(order-item freight value)**

Then:

> **Average Freight per Order = SUM(Order Freight) / Completed Commercial Orders**

**Natural Grain:**
Order

**Important Rule:**
Freight must be aggregated from order-item grain before calculating the order-level average.

**Expected Source / Model:**
`fact_order_items` → order aggregation → `mart_operations`

**Business Owner:**
Operations & Logistics / Finance

**Supports:**
BQ-06, BQ-07

---

## KPI-026 — Freight-to-GMV Ratio

**Status:** Validated

**Business Definition:**
Freight value relative to merchandise transaction value.

**Formula:**

> **Freight-to-GMV Ratio = Total Freight Value / GMV**

**Natural Grain:**
Compatible aggregated analytical population

**Primary Dimensions:**

* product category;
* seller;
* geography;
* analytical period.

**Important Rule:**
Both numerator and denominator must refer to the same analytical population and compatible grain.

**Expected Source / Model:**
`mart_commercial`, `mart_operations`

**Business Owner:**
Finance / Operations & Logistics

**Supports:**
BQ-06, BQ-07

---

## KPI-027 — Carrier Handoff Time

**Status:** Revised

**Business Definition:**
Elapsed time between recorded order approval and handoff to the logistics carrier for orders with chronologically valid timestamps.

**Formula:**

> **Carrier Handoff Time = Carrier Handoff Timestamp − Order Approval Timestamp**

**Natural Grain:**
Order

**Analytical Population:**
POP-DEL-04 — Sequence-Valid Operational Orders

Eligibility requires:

* order_approved_at is available;
* order_delivered_carrier_date is available;
* order_delivered_carrier_date >= order_approved_at.

**Data Quality Rationale:**
Source profiling identified 1,359 records in which carrier handoff occurs before recorded order approval.

These records remain preserved and flagged but are excluded from this duration calculation because they would produce a negative operational interval.

**Expected Source / Model:**
`fact_orders` → `mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-07

---

## KPI-028 — Carrier Delivery Time

**Status:** Revised

**Business Definition:**
Elapsed time between carrier handoff and confirmed customer delivery for orders with chronologically valid timestamps.

**Formula:**

> **Carrier Delivery Time = Customer Delivery Timestamp − Carrier Handoff Timestamp**

**Natural Grain:**
Order

**Analytical Population:**
POP-DEL-04 — Sequence-Valid Operational Orders

**Eligibility requires:**

* order_delivered_carrier_date is available;
* order_delivered_customer_date is available;
* order_delivered_customer_date >= order_delivered_carrier_date.

**Data Quality Rationale:**
Source profiling identified 23 records in which customer delivery occurs before the recorded carrier handoff.

These records remain preserved and flagged but are excluded from this duration calculation.

**Expected Source / Model:**
`fact_orders` → `mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-07

---

# 8. Customer Experience KPIs

## KPI-029 — Average Review Score

**Status:** Validated

**Business Definition:**
Average customer review score across valid observed review records.

**Formula:**

> **Average Review Score = AVG(review_score)**

**Natural Grain:**
Review

**Analytical Population:**
POP-REV-01 — Valid Review Records

Eligibility requires:

review_score BETWEEN 1 AND 5

Source profiling confirmed that all 99,224 observed review records contain scores within the valid 1–5 range.

**Important Rule:**
This KPI remains at review grain.

Because some orders contain multiple reviews, this metric must not automatically be interpreted as an average of one review per order.

**Primary Dimensions:**

* period;
* review score; 
* other dimensions where the review-grain relationship is valid.

Order-integrated breakdowns remain subject to POP-REV-02.

**Expected Source / Model:**
Review analytical model → `mart_customer_experience`

**Business Owner:**
Customer Experience

**Supports:**
BQ-02, BQ-09, BQ-10
BR-010, BR-011

---

## KPI-030 — Low Review Rate

**Status:** Validated

**Business Definition:**
Share of valid observed review records classified as low customer-satisfaction outcomes.

**Governed Classification:**

> **Low Review = Review Score ≤ 2**

**Formula:**

> **Low Review Rate = Low Reviews / Valid Review Records**

**Natural Grain:**
Review population

**Analytical Population:**
POP-REV-01 — Valid Review Records

Source profiling confirmed that all observed review scores fall within the valid 1–5 scale.

The observed source-profile Low Review Rate is: 14.6890%

**Expected Source / Model:**
`mart_customer_experience`

**Business Owner:**
Customer Experience

**Supports:**
BQ-09, BQ-10

---

## KPI-031 — High Review Rate

**Status:** Validated

**Business Definition:**
Share of valid observed review records classified as high customer-satisfaction outcomes.

**Provisional Classification:**

> **High Review = review_score >= 4**

**Formula:**

> **High Review Rate = High Reviews / Valid Review Records**

**Natural Grain:**
Review population

**Analytical Population:**
POP-REV-01 — Valid Review Records

The observed source-profile High Review Rate is: 77.0680%

**Expected Source / Model:**
`mart_customer_experience`

**Business Owner:**
Customer Experience

**Supports:**
BQ-09, BQ-10

---

## KPI-032 — Review Score Gap: Late vs On-Time Delivery

**Status:** Provisional

**Business Definition:**
Difference in average customer review score between late and on-time/early delivered orders.

**Formula:**

> **Review Score Gap = Average Review Score (Late) − Average Review Score (On Time/Early)**

**Natural Grain:**
Delivery-performance group

**Interpretation:**
A negative value indicates that late deliveries are associated with lower average review scores.

**Important Limitation:**
This KPI measures association and must not be interpreted independently as a causal effect.

**Expected Source / Model:**
`mart_customer_experience`

**Business Owner:**
Customer Experience / Operations & Logistics

**Supports:**
BQ-09
BR-011

---

## KPI-033 — Low Review Rate: Late Delivery

**Status:** Provisional

**Business Definition:**
Share of reviews classified as low-score outcomes among late delivered orders.

**Formula:**

> **Low Review Rate (Late) = Low Reviews for Late Orders / Valid Reviews for Late Orders**

**Natural Grain:**
Late-delivery review population

**Expected Source / Model:**
`mart_customer_experience`

**Business Owner:**
Customer Experience / Operations & Logistics

**Supports:**
BQ-09, BQ-10

---

# 9. Metric Interpretation & Quality Rules

### 9.1 Population Consistency

Numerators and denominators used in ratios must represent compatible analytical populations.

For example:

> `Late Delivery Rate`

must not divide late delivered orders by all marketplace orders, including canceled or undelivered orders.

---

### 9.2 Grain Consistency

Metrics must be aggregated to compatible grains before they are combined.

Example:

`payment_value` at payment grain must not be joined directly to multiple order items and subsequently summed without prior aggregation.

---

### 9.3 Missing Data

Missing values must remain distinguishable from valid zero values.

Examples:

* missing review score ≠ review score of zero;
* missing freight value ≠ zero freight;
* missing delivery timestamp ≠ zero delivery time.

---

### 9.4 Partial Observation Periods

Incomplete months or other partial periods must be identified before calculating or interpreting growth metrics.

---

### 9.5 Small-Sample Interpretation

Seller, category, city, or other segmented performance metrics may be unstable when based on very small numbers of observations.

Minimum-volume thresholds may therefore be applied when producing rankings or comparative analyses.

Any such threshold must be documented.

---

### 9.6 Statistical Significance vs Business Significance

A statistically significant difference does not automatically imply meaningful business impact.

Where inferential analysis is used, interpretation should consider:

* effect size;
* confidence interval;
* sample size;
* practical magnitude;
* business relevance.

---

### 9.7 Association vs Causation

Observational relationships must not be presented as causal effects unless the analytical design supports a causal interpretation.

---

### 9.8 Metric Validation

A KPI moves from **Provisional** to **Validated** only after:

1. relevant source fields have been profiled;
2. expected grain has been confirmed;
3. analytical population has been defined;
4. calculation logic has been tested;
5. edge cases and missing data have been reviewed.

---

# 10. KPI Traceability Matrix

| KPI Group                  | KPI IDs            | Primary Business Questions | Planned Analytical Layer   | Planned Dashboard Area           |
| -------------------------- | ------------------ | -------------------------- | -------------------------- | -------------------------------- |
| **Executive Performance**  | KPI-001 to KPI-005 | BQ-01, BQ-02               | `mart_executive`           | Executive Overview               |
| **Customer Growth**        | KPI-006 to KPI-012 | BQ-02, BQ-03               | `mart_customer`            | Customer Intelligence            |
| **Customer Segmentation**  | KPI-013 to KPI-015 | BQ-04                      | `mart_customer`            | Customer Intelligence            |
| **Commercial Performance** | KPI-016 to KPI-021 | BQ-05, BQ-06               | `mart_commercial`          | Commercial Performance           |
| **Operations & Logistics** | KPI-022 to KPI-028 | BQ-06, BQ-07, BQ-08        | `mart_operations`          | Operations & Customer Experience |
| **Customer Experience**    | KPI-029 to KPI-033 | BQ-02, BQ-09, BQ-10        | `mart_customer_experience` | Operations & Customer Experience |

---

# 11. KPI Validation Lifecycle

KPI governance will follow the lifecycle below:

> **Proposed → Profiled → Validated → Implemented → Tested → Published**

### Proposed

Initial business definition established from project requirements.

### Profiled

Underlying source fields and distributions have been examined.

### Validated

Population, grain, edge cases, and business interpretation have been confirmed.

### Implemented

Metric logic has been implemented in the governed analytical layer.

### Tested

Calculation and data-quality expectations have been validated.

### Published

Metric is available to approved analytical outputs such as marts, notebooks, or dashboards.

Any material change after publication must be documented and version-controlled.

# 12. Validated Analytical Population Rules

Source profiling confirmed that different analytical questions require different eligible record populations.

The platform will therefore not use a single universal **valid order** filter.

Instead, governed analytical populations are defined according to the business meaning, source grain, and data-quality requirements of each metric.

Each KPI must reference the appropriate population before it can be classified as **Validated**.

---

## 12.1 Population Governance Principles

### Population-Specific Eligibility

A record may be valid for one analytical purpose and invalid or unavailable for another.

For example:

- an order may be valid for order-status reporting but not for completed-sales analysis;
- a delivered order may be valid for GMV but unavailable for a delivery-duration metric if the required delivery timestamp is missing;
- an order without a review remains valid commercially but is unavailable for review-score analysis;
- a payment reconciliation exception does not invalidate the underlying merchandise transaction.

Therefore, records must not be globally removed from the analytical platform solely because they fail one metric-specific condition.

---

### Preservation Before Exclusion

Source records must remain preserved in raw, staging, and appropriate warehouse layers.

Metric-specific exclusions should occur through explicit analytical population rules rather than destructive source cleaning.

---

### Explicit Denominators

Ratio KPIs must document the exact population represented by their denominator.

For example:

> **Late Delivery Rate**

must divide late delivered orders by delivered orders with sufficient actual and estimated delivery information, not by all marketplace orders.

---

### Grain Compatibility

Population definitions must preserve the natural grain of the underlying metric.

Examples:

- GMV originates at order-item grain;
- order counts originate at order grain;
- payment metrics originate at payment grain;
- customer lifecycle metrics originate at persistent-customer grain;
- review metrics originate at review grain unless an explicit order-level review rule is applied.

---

# 13. Governed Analytical Populations

## POP-ORD-01 — All Observed Orders

**Status:** Validated

**Purpose:**  
Represent the complete observed order population for source-level order monitoring and status analysis.

**Eligibility Rule:**

> Include every row from the Orders source.

**Observed Population:**

> 99,441 orders

**Observed Status Values:**

- `delivered`
- `shipped`
- `canceled`
- `unavailable`
- `invoiced`
- `processing`
- `created`
- `approved`

**Primary Uses:**

- order-status distribution;
- source completeness analysis;
- order lifecycle monitoring;
- denominator when explicitly measuring the complete observed order population.

**Not Appropriate For:**

- GMV;
- completed-order AOV;
- delivered-order logistics KPIs;
- repeat-purchase analysis.

---

## POP-COM-01 — Completed Commercial Orders

**Status:** Validated

**Purpose:**  
Represent completed marketplace transactions for core commercial reporting.

**Eligibility Rule:**

> `order_status = 'delivered'`

and the order must have at least one corresponding order-item record.

Source profiling confirmed that all delivered orders are represented in Order Items.

**Rationale:**

Canceled, unavailable, created, processing, invoiced, approved, or still-shipped orders should not automatically contribute to completed commercial performance.

Using delivered orders provides a consistent completed-transaction population for executive marketplace metrics.

**Primary Uses:**

- GMV;
- Valid Orders;
- AOV;
- Items Sold;
- Category GMV;
- Seller GMV;
- commercial customer counts;
- commercial mix analysis.

**Important Interpretation:**

Completed commercial transaction value remains **GMV**, not accounting revenue or profit.

---

## POP-CUST-01 — Observed Purchasing Customers

**Status:** Validated

**Purpose:**  
Define the customer population used for customer lifecycle and behavioral analytics.

**Eligibility Rule:**

A persistent customer must have at least one order belonging to:

> `POP-COM-01 — Completed Commercial Orders`

Customer identity must be determined using:

> `customer_unique_id`

rather than transaction-specific `customer_id`.

**Primary Uses:**

- Active Customers;
- New Customers;
- Repeat Customers;
- Repeat Purchase Rate;
- Orders per Customer;
- acquisition cohorts;
- retention;
- RFM segmentation;
- observed customer monetary value.

**Important Limitation:**

The first purchase observed in the dataset cannot be assumed to represent the customer's true lifetime first purchase.

---

## POP-DEL-01 — Delivered Orders

**Status:** Validated

**Purpose:**  
Represent completed deliveries for logistics and fulfillment analysis.

**Eligibility Rule:**

> `order_status = 'delivered'`

**Observed Population:**

> 96,478 orders

**Primary Uses:**

- delivery-data completeness analysis;
- fulfillment monitoring;
- base population for more restrictive delivery KPI populations.

**Important Rule:**

Delivered status alone does not guarantee that every operational timestamp is available.

---

## POP-DEL-02 — Delivery Lead-Time Eligible Orders

**Status:** Validated

**Purpose:**  
Define the eligible population for customer delivery lead-time calculations.

**Eligibility Rules:**

- order belongs to `POP-DEL-01`;
- `order_purchase_timestamp` is available;
- `order_delivered_customer_date` is available.

**Observed Population:**

> 96,470 orders

**Formula Supported:**

> **Delivery Lead Time = Customer Delivery Timestamp − Purchase Timestamp**

Source profiling found no customer-delivery-before-purchase violations in the comparable population.

**Primary Uses:**

- median delivery lead time;
- delivery-time percentiles;
- delivery lead-time distributions.

---

## POP-DEL-03 — Delivery Estimate Comparable Orders

**Status:** Validated

**Purpose:**  
Define the eligible population for comparing actual delivery against estimated delivery.

**Eligibility Rules:**

- order belongs to `POP-DEL-01`;
- `order_delivered_customer_date` is available;
- `order_estimated_delivery_date` is available.

**Observed Population:**

> 96,470 orders

**Primary Uses:**

- Days Early / Late;
- Late Delivery Rate;
- delivery-estimate accuracy.

**Validated Late Classification:**

> **Late:** Actual Delivery Timestamp > Estimated Delivery Timestamp

> **On Time / Early:** Actual Delivery Timestamp ≤ Estimated Delivery Timestamp

Initial profiling identified:

> 7,826 late delivered orders

corresponding to an observed:

> **8.1124% late-delivery rate**

within the validated comparison population.

---

## POP-DEL-04 — Sequence-Valid Operational Orders

**Status:** Validated as a required quality rule

**Purpose:**  
Provide valid populations for intermediate operational-duration metrics involving approval, carrier handoff, and customer delivery.

Source profiling identified:

- 1,359 orders where carrier handoff precedes approval;
- 23 orders where customer delivery precedes carrier handoff.

Therefore, intermediate duration metrics must require chronologically valid timestamp sequences.

Examples include:

### Approval-to-Carrier Population

Requires:

> `order_delivered_carrier_date >= order_approved_at`

### Carrier-to-Customer Population

Requires:

> `order_delivered_customer_date >= order_delivered_carrier_date`

**Important Rule:**

The anomalous source records must remain preserved.

They are excluded only from metrics whose mathematical interpretation requires valid chronological ordering.

---

## POP-PAY-01 — Valid Payment Records

**Status:** Validated

**Purpose:**  
Represent observed payment events at their natural source grain.

**Validated Grain:**

> one row per `order_id + payment_sequential`

**Eligibility Rule:**

Use observed payment records while preserving their payment-sequence grain.

**Primary Uses:**

- payment-method analysis;
- installments analysis;
- payment-value analysis;
- payment-record multiplicity.

**Important Rule:**

Payment measures must be aggregated to order grain before being combined with order-level or order-item analytical datasets.

---

## POP-PAY-02 — Payment Reconciliation Comparable Orders

**Status:** Validated

**Purpose:**  
Compare aggregated payment values against aggregated item price plus freight.

**Eligibility Rules:**

An order must have:

- at least one order-item record;
- at least one payment record.

**Observed Comparable Population:**

> 98,665 orders

Monetary reconciliation is calculated using integer cents.

**Observed Results:**

- 98,089 orders reconcile exactly;
- 98,362 orders reconcile within one cent;
- 303 orders differ by more than one cent.

**Validated One-Cent Reconciliation Rate:**

> **99.6929%**

**Important Rule:**

Payment reconciliation exceptions do not modify the definitions of GMV or Freight Value.

`payment_value`, item price, and freight remain separate source measures.

---

## POP-REV-01 — Valid Review Records

**Status:** Validated

**Purpose:**  
Represent observed customer-review records with valid score values.

**Eligibility Rule:**

> `review_score` must be between 1 and 5 inclusive.

**Observed Population:**

> 99,224 valid review records

Source profiling identified:

> 0 invalid review scores.

**Primary Uses:**

- review-score distribution;
- Average Review Score;
- Low Review Rate;
- High Review Rate.

**Validated Satisfaction Classifications:**

> **Low Review:** `review_score <= 2`

> **High Review:** `review_score >= 4`

Initial observed rates are:

- Low Review Rate: **14.6890%**
- High Review Rate: **77.0680%**

---

## POP-REV-02 — Order-Integrated Review Population

**Status:** Provisional

**Purpose:**  
Support analyses combining review outcomes with order-level commercial or logistics characteristics.

Source profiling confirmed that:

- 547 orders contain more than one review record;
- a single order may contain up to 3 review records;
- `review_id` alone is not a unique row identifier;
- `review_id + order_id` uniquely identifies source review rows.

Because review data is not strictly one-to-one with Orders, an explicit review consolidation or analytical-grain rule must be established before order-level review KPIs are considered fully validated.

**Pending Decision:**

The project must determine whether cross-domain analysis should:

- remain at review grain;
- select a canonical review per order;
- or aggregate multiple reviews to an explicitly defined order-level measure.

Until that decision is documented and implemented, order-integrated review metrics remain provisional.

---

## POP-GEO-01 — Standardized Geographic Population

**Status:** Provisional

**Purpose:**  
Support consistent geographic enrichment of customers and sellers.

Raw geolocation cannot be used directly because profiling identified:

- 1,000,163 source records;
- 19,015 distinct ZIP-code prefixes;
- 261,831 exact duplicate rows beyond the first occurrence;
- 17,972 ZIP prefixes represented by multiple rows;
- up to 1,146 geolocation observations for a single ZIP prefix.

A standardized geographic model must be implemented before geographic KPI breakdowns are considered validated.

**Important Rule:**

Direct analytical joins from customer or seller records to raw geolocation by ZIP-code prefix are prohibited.

---

## POP-TIME-01 — Comparable Calendar Periods

**Status:** Provisional

**Purpose:**  
Define periods eligible for growth and time-series comparisons.

Source profiling confirmed that order activity spans a finite historical observation window.

Boundary periods may represent incomplete calendar periods and must not automatically be interpreted as comparable full months.

Before MoM or YoY growth KPIs are finalized, the project must identify:

- complete calendar periods;
- partial boundary periods;
- any periods with abnormal source coverage.

**Primary Uses:**

- GMV Growth;
- Orders Growth;
- time-series trend analysis.

---

# 14. Population-to-KPI Governance

The analytical populations above become part of the formal KPI definition.

A KPI can move from **Provisional** to **Validated** only when:

1. its business definition is supported by the available source data;
2. its natural grain has been validated;
3. its analytical population has been defined;
4. required source fields have been profiled;
5. relevant missing values and exceptions have documented treatment;
6. calculation logic is reproducible;
7. the KPI does not rely on an unresolved modeling decision.

This means KPI validation may occur incrementally.

For example:

> **Delivery Lead Time**

can be validated using `POP-DEL-02`, while:

> **Review Score Gap: Late vs On-Time Delivery**

must remain provisional until the order-integrated review population in `POP-REV-02` is finalized.

# 15. KPI-by-KPI Validation Matrix

The following matrix evaluates each governed KPI against the source-profiling evidence and the analytical populations defined in Sections 12–14.

The validation decision applies to the **metric definition and analytical population**.

A KPI classified as **Validated** may still require implementation, automated testing, and publication before completing the full KPI lifecycle defined in Section 11.

---

## 15.1 Validation Status Definitions

| Status          | Meaning                                                                                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Validated**   | Business definition, grain, source fields, analytical population, and material data-quality treatment are sufficiently defined to support implementation |
| **Revised**     | The original KPI remains relevant but requires a material change to its definition or eligible population based on profiling evidence                    |
| **Provisional** | One or more important modeling, population, temporal, geographic, or analytical decisions remain unresolved                                              |

---

## 15.2 KPI Validation Decisions

| KPI         | KPI Name                                   | Validation Decision | Governed Population          | Validation Rationale                                                                                                                                                                   |
| ----------- | ------------------------------------------ | ------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **KPI-001** | Gross Merchandise Value (GMV)              | **Validated**       | `POP-COM-01`                 | Order-item price is complete and non-negative. Order-item grain is validated. GMV is explicitly separated from freight and payment value.                                              |
| **KPI-002** | Valid Orders                               | **Revised**         | `POP-COM-01`                 | The term *Valid Orders* was too generic. For core commercial reporting, the metric must represent completed commercial orders with `order_status = 'delivered'`.                       |
| **KPI-003** | Average Order Value (AOV)                  | **Validated**       | `POP-COM-01`                 | GMV and completed-order count now have compatible and explicitly governed populations.                                                                                                 |
| **KPI-004** | GMV Growth Rate                            | **Provisional**     | `POP-TIME-01`                | The metric formula is valid, but comparable full calendar periods and incomplete boundary periods have not yet been finalized.                                                         |
| **KPI-005** | Orders Growth Rate                         | **Provisional**     | `POP-TIME-01`                | Same unresolved calendar-period comparability requirement as KPI-004.                                                                                                                  |
| **KPI-006** | Active Customers                           | **Validated**       | `POP-CUST-01`                | Persistent customer identity is confirmed through `customer_unique_id`, and the valid purchasing population is defined.                                                                |
| **KPI-007** | New Customers                              | **Validated**       | `POP-CUST-01`                | First observed completed purchase can be calculated reproducibly using the persistent customer identifier. The finite observation-window limitation remains documented.                |
| **KPI-008** | Repeat Customers                           | **Validated**       | `POP-CUST-01`                | Multiple customer records per `customer_unique_id` are empirically confirmed, supporting persistent-customer repeat-purchase logic.                                                    |
| **KPI-009** | Repeat Purchase Rate                       | **Validated**       | `POP-CUST-01`                | Numerator and denominator are explicitly defined at persistent-customer grain. Observation-window bias remains a documented limitation.                                                |
| **KPI-010** | Orders per Customer                        | **Validated**       | `POP-CUST-01`                | Completed commercial orders and persistent customers can be combined at a controlled customer-period grain.                                                                            |
| **KPI-011** | Customer GMV                               | **Validated**       | `POP-CUST-01` + `POP-COM-01` | Order-item GMV can be aggregated through completed orders to persistent customer grain without relying on payment values.                                                              |
| **KPI-012** | Cohort Retention Rate                      | **Validated**       | `POP-CUST-01`                | Acquisition cohort is defined by first observed completed purchase month and retention by subsequent completed purchases. Later cohorts remain subject to shorter observation windows. |
| **KPI-013** | Customer Recency                           | **Provisional**     | `POP-CUST-01`                | Purchase history is valid, but the analytical reference date for RFM scoring has not yet been formally governed.                                                                       |
| **KPI-014** | Customer Frequency                         | **Validated**       | `POP-CUST-01`                | Frequency can be calculated as distinct completed commercial orders per persistent customer.                                                                                           |
| **KPI-015** | Customer Monetary Value                    | **Validated**       | `POP-CUST-01` + `POP-COM-01` | Observed cumulative GMV is supported at persistent-customer grain and remains explicitly distinct from predictive CLV.                                                                 |
| **KPI-016** | Items Sold                                 | **Validated**       | `POP-COM-01`                 | `order_id + order_item_id` uniquely identifies item records and completed-order membership provides the governed commercial population.                                                |
| **KPI-017** | Category GMV                               | **Validated**       | `POP-COM-01`                 | Product category and item-price relationships are valid. Missing and untranslated categories must be retained explicitly.                                                              |
| **KPI-018** | Category GMV Share                         | **Validated**       | `POP-COM-01`                 | Category GMV and total GMV use the same governed commercial population.                                                                                                                |
| **KPI-019** | Seller GMV                                 | **Validated**       | `POP-COM-01`                 | Seller references have 100% referential coverage and item-level GMV can be aggregated safely by seller.                                                                                |
| **KPI-020** | Seller Order Volume                        | **Validated**       | `POP-COM-01`                 | Distinct order counting by seller is supported. Multi-seller orders are explicitly recognized and seller order counts must not be summed to obtain marketplace orders.                 |
| **KPI-021** | Seller Customer Count                      | **Validated**       | `POP-COM-01` + `POP-CUST-01` | Seller items can be linked through completed orders to persistent customer identifiers.                                                                                                |
| **KPI-022** | Delivery Lead Time                         | **Validated**       | `POP-DEL-02`                 | Purchase and customer-delivery timestamps support 96,470 valid comparisons, with no customer-delivery-before-purchase violations.                                                      |
| **KPI-023** | Days Early / Late                          | **Validated**       | `POP-DEL-03`                 | Actual and estimated delivery timestamps support a governed comparison population and an explicit signed interpretation.                                                               |
| **KPI-024** | Late Delivery Rate                         | **Validated**       | `POP-DEL-03`                 | Denominator is explicitly restricted to delivered orders with valid actual and estimated timestamps.                                                                                   |
| **KPI-025** | Average Freight Value per Order            | **Validated**       | `POP-COM-01`                 | Freight is complete and non-negative at item grain and can be aggregated to order grain before averaging.                                                                              |
| **KPI-026** | Freight-to-GMV Ratio                       | **Validated**       | `POP-COM-01`                 | Freight and GMV originate from compatible order-item populations and can be aggregated consistently.                                                                                   |
| **KPI-027** | Carrier Handoff Time                       | **Revised**         | `POP-DEL-04`                 | 1,359 carrier-handoff-before-approval exceptions invalidate unrestricted duration calculations. The metric must use chronology-valid records only.                                     |
| **KPI-028** | Carrier Delivery Time                      | **Revised**         | `POP-DEL-04`                 | 23 customer-delivery-before-carrier-handoff exceptions require an explicit valid-sequence population.                                                                                  |
| **KPI-029** | Average Review Score                       | **Validated**       | `POP-REV-01`                 | All 99,224 observed review scores fall within the valid 1–5 source scale. The KPI remains at review grain.                                                                             |
| **KPI-030** | Low Review Rate                            | **Validated**       | `POP-REV-01`                 | `review_score <= 2` is adopted as the governed project definition of a low review and all observed scores are valid.                                                                   |
| **KPI-031** | High Review Rate                           | **Validated**       | `POP-REV-01`                 | `review_score >= 4` is adopted as the governed project definition of a high review.                                                                                                    |
| **KPI-032** | Review Score Gap: Late vs On-Time Delivery | **Provisional**     | `POP-REV-02` + `POP-DEL-03`  | Review-to-order integration remains unresolved because 547 orders contain multiple review records.                                                                                     |
| **KPI-033** | Low Review Rate: Late Delivery             | **Provisional**     | `POP-REV-02` + `POP-DEL-03`  | The late-delivery population is validated, but the rule for integrating multiple reviews per order remains unresolved.                                                                 |

---

# 16. KPI Validation Summary

The 33 governed KPIs currently have the following validation status:

| Validation Status | KPI Count |
| ----------------- | --------: |
| **Validated**     |        25 |
| **Revised**       |         3 |
| **Provisional**   |         5 |
| **Total**         |    **33** |

The results demonstrate that profiling did not simply convert all planned KPIs into validated measures.

Instead, empirical source behavior resulted in three distinct outcomes:

> **25 KPIs can proceed with their definitions and governed populations.**

> **3 KPIs require changes based on observed source conditions.**

> **5 KPIs remain intentionally unresolved until additional modeling decisions are completed.**

This distinction preserves the meaning of KPI validation as an evidence-based governance process.

---

# 17. Revised KPI Decisions

## KPI-002 — Valid Orders

The original term **Valid Orders** is too broad because source profiling confirmed that analytical eligibility depends on the business context.

For executive commercial reporting, KPI-002 will be revised to represent:

> **Completed Commercial Orders**

with the definition:

> **Completed Commercial Orders = COUNT(DISTINCT order_id)**

for orders belonging to:

> `POP-COM-01 — Completed Commercial Orders`

The underlying Orders dataset will continue to preserve all observed statuses.

---

## KPI-027 — Carrier Handoff Time

The original definition remains conceptually useful but requires an explicit sequence-valid population.

The revised calculation is:

> **Carrier Handoff Time = Carrier Handoff Timestamp − Order Approval Timestamp**

only where:

> `Carrier Handoff Timestamp >= Order Approval Timestamp`

Records violating this sequence remain preserved and flagged but are not eligible for this duration metric.

---

## KPI-028 — Carrier Delivery Time

The original definition remains conceptually useful but requires an explicit sequence-valid population.

The revised calculation is:

> **Carrier Delivery Time = Customer Delivery Timestamp − Carrier Handoff Timestamp**

only where:

> `Customer Delivery Timestamp >= Carrier Handoff Timestamp`

Records violating this sequence remain preserved and flagged but are not eligible for this duration metric.

---

# 18. Remaining Provisional KPI Decisions

Five KPIs remain provisional for explicit reasons.

## KPI-004 and KPI-005 — Growth Metrics

Before GMV Growth and Orders Growth can be validated, the project must determine which calendar periods represent complete and comparable observation windows.

Required next decision:

> Finalize `POP-TIME-01 — Comparable Calendar Periods`.

---

## KPI-013 — Customer Recency

The calculation requires a governed analytical reference date.

Possible approaches include:

* final complete commercial date in the observation window;
* day immediately following the final complete observation period;
* another documented analytical snapshot date.

The choice must be made before RFM segmentation is implemented.

---

## KPI-032 and KPI-033 — Order-Integrated Review Metrics

The source contains multiple review records for some orders.

Before customer-experience metrics are combined with delivery outcomes, the project must define how multiple reviews associated with the same order should be handled.

Possible approaches include:

* preserve review grain and allow multiple review observations per order;
* define a canonical review selection rule;
* aggregate review records to an order-level outcome.

The selected method must preserve analytical transparency and avoid unintended weighting of orders with multiple reviews.

---

# 19. Geographic Validation Dependency

Core KPI definitions may be validated even when a geographic breakdown remains provisional.

For example:

> **GMV** is validated as a marketplace metric.

However:

> **GMV by standardized geographic location**

depends on completion of:

> `POP-GEO-01 — Standardized Geographic Population`.

Therefore, KPI status and dimension-enrichment status must be treated independently.

The same principle applies to seller, customer, freight, delivery, and review KPIs that may later be segmented geographically.

---

# 20. Validation vs Implementation

A **Validated** KPI is not automatically a finished KPI.

The remaining lifecycle is:

> **Validated → Implemented → Tested → Published**

Implementation will require:

* dimensional warehouse models;
* governed transformation logic;
* analytical marts;
* automated tests;
* reconciliation against profiling expectations;
* dashboard integration where applicable.

The KPI validation matrix therefore authorizes implementation but does not replace implementation testing.
