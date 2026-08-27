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

**Status:** Provisional

**Business Definition:**
Total merchandise transaction value represented by the price of eligible order items during the analytical period.

**Formula:**

> **GMV = SUM(order item price)**

**Natural Grain:**
Order item

**Analytical Population:**
Order items associated with orders included in the valid commercial analytical population.

The exact eligible order statuses will be confirmed during data profiling.

**Excludes by Default:**

* freight value;
* payment value duplicated across payment records;
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

## KPI-002 — Valid Orders

**Status:** Provisional

**Business Definition:**
Number of distinct marketplace orders included in the relevant analytical population.

**Formula:**

> **Valid Orders = COUNT(DISTINCT order_id)**

**Natural Grain:**
Order

**Analytical Population:**
Orders satisfying the status and quality conditions defined for the specific analysis.

The primary executive order population will be confirmed during source-data profiling.

**Primary Dimensions:**

* purchase date;
* customer geography;
* product category;
* seller.

**Expected Source / Model:**
`fact_orders`

**Business Owner:**
Executive Management

**Supports:**
BQ-01, BQ-02, BQ-03, BQ-05
BR-001, BR-002, BR-003, BR-005

---

## KPI-003 — Average Order Value (AOV)

**Status:** Provisional

**Business Definition:**
Average merchandise transaction value generated by an eligible marketplace order.

**Formula:**

> **AOV = GMV / Valid Orders**

**Natural Grain:**
Order after item-level GMV has been aggregated to order level.

**Important Rule:**
AOV must not be calculated as the average order-item price.

**Analytical Population:**
Same commercial population used for GMV and Valid Orders.

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
Percentage change in valid marketplace orders between comparable periods.

**Formula:**

> **Orders Growth = (Current Period Orders − Previous Comparable Period Orders) / Previous Comparable Period Orders**

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

**Business Definition:**
Average number of valid marketplace orders associated with an active customer.

**Formula:**

> **Orders per Customer = Valid Orders / Active Customers**

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

**Business Definition:**
Number of eligible order-item records associated with valid marketplace orders.

**Formula:**

> **Items Sold = COUNT(valid order items)**

Where `order_item_id` represents the sequence of an item within an order, each valid order-item record is treated as one sold item unless profiling identifies a different interpretation.

**Natural Grain:**
Order item

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

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

**Status:** Provisional

**Business Definition:**
Average freight value associated with a valid marketplace order.

**Formula:**

First aggregate freight to order grain:

> **Order Freight = SUM(order-item freight value)**

Then:

> **Average Freight per Order = SUM(Order Freight) / Valid Orders**

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

**Status:** Provisional

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

**Status:** Provisional

**Business Definition:**
Elapsed time between order approval and handoff to the logistics carrier.

**Formula:**

> **Carrier Handoff Time = Carrier Handoff Timestamp − Order Approval Timestamp**

**Natural Grain:**
Order

**Analytical Population:**
Orders with valid approval and carrier-handoff timestamps.

**Expected Source / Model:**
`fact_orders` → `mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-07

---

## KPI-028 — Carrier Delivery Time

**Status:** Provisional

**Business Definition:**
Elapsed time between carrier handoff and confirmed customer delivery.

**Formula:**

> **Carrier Delivery Time = Customer Delivery Timestamp − Carrier Handoff Timestamp**

**Natural Grain:**
Order

**Expected Source / Model:**
`fact_orders` → `mart_operations`

**Business Owner:**
Operations & Logistics

**Supports:**
BQ-07

---

# 8. Customer Experience KPIs

## KPI-029 — Average Review Score

**Status:** Provisional

**Business Definition:**
Average customer review score associated with eligible marketplace orders.

**Formula:**

> **Average Review Score = AVG(valid review score)**

**Natural Grain:**
Review / order relationship

**Analytical Population:**
Reviews containing a valid score within the source-defined scale.

**Important Rule:**
Source profiling must verify whether orders can contain multiple review records before the final analytical grain is confirmed.

**Primary Dimensions:**

* period;
* delivery status;
* product category;
* seller;
* customer geography.

**Expected Source / Model:**
Review analytical model → `mart_customer_experience`

**Business Owner:**
Customer Experience

**Supports:**
BQ-02, BQ-09, BQ-10
BR-010, BR-011

---

## KPI-030 — Low Review Rate

**Status:** Provisional

**Business Definition:**
Share of valid reviews classified as low customer-satisfaction outcomes.

**Provisional Classification:**

> **Low Review = Review Score ≤ 2**

**Formula:**

> **Low Review Rate = Low Reviews / Valid Reviews**

**Natural Grain:**
Review population

**Important Rule:**
The threshold will be validated against the observed review-score distribution before the KPI is finalized.

**Expected Source / Model:**
`mart_customer_experience`

**Business Owner:**
Customer Experience

**Supports:**
BQ-09, BQ-10

---

## KPI-031 — High Review Rate

**Status:** Provisional

**Business Definition:**
Share of valid reviews classified as high customer-satisfaction outcomes.

**Provisional Classification:**

> **High Review = Review Score ≥ 4**

**Formula:**

> **High Review Rate = High Reviews / Valid Reviews**

**Natural Grain:**
Review population

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
