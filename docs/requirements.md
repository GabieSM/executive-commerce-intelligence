# Requirements Specification

## Executive Commerce Intelligence Platform

### 1. Purpose

This document defines the business, data, analytical, and non-functional requirements for the Executive Commerce Intelligence Platform.

The requirements translate the objectives and business questions defined in the Business Case into explicit capabilities that the analytical solution must provide.

Each requirement is assigned a unique identifier to support traceability across data models, transformations, analytical outputs, tests, and dashboard components.

---

### 2. Requirement Classification

Requirements are organized into four categories:

| Type                           | Prefix | Description                                                                                                                 |
| ------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Business Requirement**       | BR     | Defines the business capability or decision-support need that the platform must satisfy                                     |
| **Data Requirement**           | DR     | Defines the data, relationships, fields, quality conditions, or historical information required                             |
| **Analytical Requirement**     | AR     | Defines how metrics, segments, cohorts, statistical analyses, or other analytical outputs must be calculated                |
| **Non-Functional Requirement** | NFR    | Defines requirements related to reproducibility, maintainability, quality, documentation, security, and technical operation |

---

### 3. Business Requirements

#### BR-001 — Executive Performance Monitoring

**Requirement:**
Executive Management must be able to monitor the evolution of core marketplace performance indicators over time, including GMV, orders, active customers, and average order value.

**Supports:** BQ-01, BQ-02
**Primary Stakeholder:** Executive Management

---

#### BR-002 — Growth Driver Analysis

**Requirement:**
Executive Management must be able to identify the major contributors to changes in marketplace performance, including order volume, average order value, customer acquisition, repeat purchasing, product mix, and geography.

**Supports:** BQ-01
**Primary Stakeholder:** Executive Management

---

#### BR-003 — Customer Growth & Retention

**Requirement:**
Customer and Growth teams must be able to distinguish new customers from repeat customers and evaluate purchasing behavior across customer acquisition cohorts.

**Supports:** BQ-02, BQ-03
**Primary Stakeholder:** Customer / Growth Team

---

#### BR-004 — Customer Value Segmentation

**Requirement:**
The platform must enable the identification and comparison of customer segments based on purchasing recency, frequency, and monetary value.

**Supports:** BQ-04
**Primary Stakeholder:** Customer / Growth Team

---

#### BR-005 — Product & Category Performance

**Requirement:**
Commercial teams must be able to evaluate marketplace performance by product category using transaction volume, GMV, average item value, customer demand, and relevant operational indicators.

**Supports:** BQ-05, BQ-06
**Primary Stakeholder:** Commercial / Marketplace Management

---

#### BR-006 — Seller Performance

**Requirement:**
Commercial and Operations teams must be able to compare seller performance across transaction volume, GMV, delivery performance, freight characteristics, and customer-review outcomes.

**Supports:** BQ-05, BQ-06, BQ-07
**Primary Stakeholders:** Commercial / Marketplace Management, Operations & Logistics

---

#### BR-007 — Geographic Performance

**Requirement:**
Management must be able to compare commercial and operational performance across geographic markets and identify regions with strong commercial activity but weak logistics or customer-experience outcomes.

**Supports:** BQ-05, BQ-06, BQ-07
**Primary Stakeholders:** Executive Management, Commercial / Marketplace Management, Operations & Logistics

---

#### BR-008 — Logistics Performance

**Requirement:**
Operations teams must be able to monitor delivery lead times, late-delivery rates, freight characteristics, and recurring logistics bottlenecks.

**Supports:** BQ-07
**Primary Stakeholder:** Operations & Logistics

---

#### BR-009 — Delivery Estimate Accuracy

**Requirement:**
Operations teams must be able to compare estimated delivery dates with actual delivery dates and evaluate delivery-estimation accuracy across relevant business dimensions.

**Supports:** BQ-08
**Primary Stakeholder:** Operations & Logistics

---

#### BR-010 — Customer Experience Monitoring

**Requirement:**
Customer Experience teams must be able to monitor review-score performance and identify segments with disproportionately high levels of negative customer feedback.

**Supports:** BQ-02, BQ-09, BQ-10
**Primary Stakeholder:** Customer Experience

---

#### BR-011 — Operational Impact on Customer Experience

**Requirement:**
The platform must support analysis of the relationship between operational performance, particularly delivery performance, and customer-review outcomes.

**Supports:** BQ-09, BQ-10
**Primary Stakeholders:** Customer Experience, Operations & Logistics

---

#### BR-012 — Consistent Business Metrics

**Requirement:**
Business stakeholders must receive consistent metric definitions across analytical outputs so that equivalent KPIs produce the same result regardless of the dashboard, analysis, or data mart in which they are used.

**Supports:** BQ-01 to BQ-10
**Primary Stakeholder:** Data & Analytics Team

### 4. Data Requirements

The analytical solution requires reliable integration of transactional, customer, product, seller, payment, logistics, geographic, and customer-experience data.

Data requirements define the minimum information and structural conditions necessary to support the business and analytical requirements established for the platform.

---

#### DR-001 — Order-Level Transaction Data

**Requirement:**
The platform must contain one identifiable record for each marketplace order, including its customer relationship, order status, purchase timestamp, approval timestamp, carrier handoff timestamp, actual delivery timestamp, and estimated delivery timestamp where available.

**Required for:** BR-001, BR-002, BR-003, BR-008, BR-009, BR-011
**Expected source:** Orders data

**Key fields include:**

* order identifier;
* customer identifier;
* order status;
* purchase timestamp;
* order approval timestamp;
* carrier delivery timestamp;
* customer delivery timestamp;
* estimated delivery timestamp.

---

#### DR-002 — Persistent Customer Identity

**Requirement:**
The platform must distinguish between transaction-level customer identifiers and persistent customer identifiers when analyzing customer behavior over time.

A persistent customer identifier must be used for repeat-purchase, cohort, frequency, and customer-value analyses.

**Required for:** BR-003, BR-004
**Expected source:** Customers data

**Business rule:**
`customer_unique_id`, or the equivalent persistent identifier available in the source data, must be used when identifying the same customer across multiple orders.

A transaction-specific `customer_id` must not be interpreted automatically as a persistent customer identity.

---

#### DR-003 — Order Item Grain

**Requirement:**
Individual products within an order must be identifiable independently so that product-category, seller, pricing, and freight analyses can be performed at order-item level.

**Required for:** BR-002, BR-005, BR-006
**Expected source:** Order Items data

The analytical model must preserve the distinction between:

> **Order grain:** one record per order

and

> **Order-item grain:** one record per item within an order.

Measures calculated at order-item level must not be aggregated together with order-level measures without explicitly accounting for differences in grain.

---

#### DR-004 — Product Attributes

**Requirement:**
Each order item must be linkable to product information required for commercial analysis, including product category and relevant product characteristics where available.

**Required for:** BR-005, BR-006
**Expected source:** Products data

Product-category information must be standardized before being used in analytical reporting.

Where category translations are available, the project must preserve both the original source category and the standardized analytical category.

---

#### DR-005 — Seller Identity

**Requirement:**
Each applicable order item must be associated with a seller identifier so that commercial and operational performance can be analyzed at seller level.

**Required for:** BR-006, BR-008
**Expected sources:** Order Items, Sellers data

Seller information must support analysis of:

* transaction volume;
* GMV;
* product mix;
* freight characteristics;
* delivery performance;
* customer-review outcomes.

---

#### DR-006 — Payment Data

**Requirement:**
The platform must preserve payment-level information associated with marketplace orders, including payment method, installment information, payment sequence, and payment value where available.

**Required for:** BR-001, BR-002
**Expected source:** Payments data

The data model must recognize that an order may contain more than one payment record.

Payment data must therefore not be joined directly to order-item-level data without controls that prevent duplication of monetary measures.

---

#### DR-007 — Customer Review Data

**Requirement:**
Customer-review outcomes must be linkable to the corresponding order so that customer-experience analysis can be performed alongside commercial and operational characteristics.

**Required for:** BR-010, BR-011
**Expected source:** Reviews data

Relevant review information includes:

* review score;
* review creation timestamp;
* review response timestamp;
* textual review information where analytically appropriate.

Textual review content is not required for the initial analytical scope but should be preserved in the raw data layer if available.

---

#### DR-008 — Delivery Performance Data

**Requirement:**
The platform must contain sufficient timestamp information to calculate delivery lead time, delivery delay, and delivery-estimation accuracy.

**Required for:** BR-008, BR-009, BR-011
**Expected source:** Orders data

At minimum, the analytical model should support calculation of:

* purchase-to-delivery time;
* carrier handoff-to-delivery time;
* estimated versus actual delivery difference;
* on-time versus late-delivery classification.

Records without the required timestamps must be identified rather than silently excluded.

---

#### DR-009 — Geographic Data

**Requirement:**
Customers and sellers must be associated with the most reliable geographic attributes available in the source data to support regional performance analysis.

**Required for:** BR-005, BR-006, BR-007, BR-008
**Expected sources:** Customers, Sellers, Geolocation data

Relevant geographic attributes may include:

* ZIP-code prefix;
* city;
* state;
* latitude;
* longitude.

Geographic transformations must account for duplicated or inconsistent geographic reference records where applicable.

---

#### DR-010 — Calendar & Time Dimensions

**Requirement:**
Transactional timestamps must support consistent analysis across calendar periods.

**Required for:** BR-001 through BR-011 where time-series analysis is applicable.

The analytical warehouse must support derived calendar attributes including:

* date;
* year;
* quarter;
* month;
* year-month;
* week;
* day of week;
* weekend indicator.

A reusable date dimension should be created so that time-based definitions remain consistent across analytical marts.

---

#### DR-011 — Order Status

**Requirement:**
Order status must be preserved and standardized because valid analytical populations may differ depending on the metric being calculated.

**Required for:** BR-001, BR-002, BR-005, BR-008

Metrics must explicitly document whether they include or exclude statuses such as:

* delivered;
* shipped;
* canceled;
* unavailable;
* invoiced;
* processing;
* approved.

No universal status filter should be assumed without reference to the metric definition.

---

#### DR-012 — Monetary Measures

**Requirement:**
The analytical platform must preserve monetary fields at their natural grain and clearly distinguish among item price, freight value, payment value, and derived transaction-value measures.

**Required for:** BR-001, BR-002, BR-004, BR-005, BR-006

Monetary measures must not be duplicated as a consequence of joins across one-to-many relationships.

Derived financial measures must document both their formula and their grain.

The project must not classify marketplace transaction value as accounting revenue or profit without source data supporting that interpretation.

---

#### DR-013 — Referential Integrity

**Requirement:**
Relationships among orders, customers, order items, products, sellers, payments, and reviews must be validated before analytical modeling.

**Required for:** All analytical requirements.

Examples of integrity checks include:

* every order customer identifier should correspond to an available customer record where expected;
* every order item should correspond to an available order;
* referenced products should exist in product data where expected;
* referenced sellers should exist in seller data where expected;
* payments and reviews should reference valid orders where expected.

Orphaned records must be identified, quantified, and documented.

---

#### DR-014 — Duplicate Detection

**Requirement:**
Potential duplicate records must be identified at the expected grain of each source dataset.

**Required for:** Data quality and analytical reliability.

Duplicate detection must distinguish between:

* true duplicate records;
* legitimate one-to-many relationships;
* repeated identifiers that are valid because the natural grain includes additional keys.

Records must not be removed solely because an identifier appears more than once without first validating the expected table grain.

---

#### DR-015 — Missing Data

**Requirement:**
Missing values in analytically relevant fields must be profiled and documented before transformation logic is implemented.

Missing information must be classified where possible as:

* structurally expected;
* operationally incomplete;
* analytically problematic;
* unknown.

Missing records or fields must not be automatically imputed, excluded, or converted to zero without an explicit analytical rule.

---

#### DR-016 — Data-Type & Domain Validation

**Requirement:**
Source columns must be validated against their expected analytical type and logical domain before being used downstream.

Examples include:

* monetary values must be numeric;
* item and freight values should not be negative unless explicitly justified;
* timestamps must be parseable;
* review scores must fall within the valid source range;
* geographic codes must conform to expected formats;
* categorical values must be profiled before standardization.

Invalid values must be surfaced through data-quality checks.

---

#### DR-017 — Temporal Consistency

**Requirement:**
Timestamp relationships must be validated for logical consistency.

Examples include:

* purchase time should not occur after customer delivery;
* carrier handoff should generally not occur after customer delivery;
* estimated delivery dates must be interpreted separately from actual timestamps;
* approval timestamps must be evaluated for chronological consistency with purchase timestamps.

Exceptions must be quantified and investigated before being excluded or corrected.

---

#### DR-018 — Raw Data Preservation

**Requirement:**
Source datasets must be preserved in an unmodified raw layer before analytical transformations are applied.

The raw layer must represent the closest reproducible copy of the original source files used by the project.

Analytical cleaning, standardization, renaming, deduplication, and business logic must occur in downstream layers rather than modifying the original source data.

---

#### DR-019 — Source Traceability

**Requirement:**
Analytical tables and metrics must be traceable back to their originating source datasets and transformation logic.

Documentation should allow an analyst to determine:

> source data → transformation → analytical model → KPI or analytical output.

This requirement will later be supported through dbt documentation, model descriptions, source definitions, and lineage.

---

#### DR-020 — Data Privacy

**Requirement:**
The project must not introduce or attempt to reconstruct personally identifiable customer information beyond what is available and necessary for the analytical objectives.

Customer behavioral analysis will use anonymized source identifiers.

No attempt will be made to identify real individuals represented in the dataset.

### 5. Analytical Requirements

Analytical requirements define how business concepts, metrics, customer segments, time-based measures, and statistical analyses must be constructed.

Unless otherwise specified, analytical outputs must be derived from documented source fields and calculated at an explicitly defined grain.

---

#### AR-001 — Gross Merchandise Value (GMV)

**Requirement:**
Marketplace transaction value must be represented using a clearly defined Gross Merchandise Value metric.

For the initial project scope:

> **GMV = Sum of order-item price values included in the valid analytical population**

Freight charges must not automatically be included in GMV.

The relevant order-status population must be defined explicitly in the KPI framework before the metric is used in reporting.

**Supports:** BR-001, BR-002, BR-005, BR-006

---

#### AR-002 — Order Count

**Requirement:**
Order volume must be calculated using distinct order identifiers rather than row counts from order-item, payment, or other one-to-many datasets.

> **Orders = COUNT(DISTINCT order_id)**

The relevant order-status population must be documented for each analytical context.

**Supports:** BR-001, BR-002, BR-003, BR-005

---

#### AR-003 — Average Order Value

**Requirement:**
Average Order Value must be calculated at order grain.

> **AOV = GMV / Number of Valid Orders**

AOV must not be calculated as the simple average of order-item prices.

**Supports:** BR-001, BR-002, BR-005

---

#### AR-004 — Active Customer

**Requirement:**
An active customer is a persistent customer identifier associated with at least one valid order during the analytical period.

> **Active Customers = COUNT(DISTINCT customer_unique_id)**

Customer-level metrics must use the persistent customer identifier defined in DR-002.

**Supports:** BR-001, BR-003, BR-004

---

#### AR-005 — New Customer

**Requirement:**
A customer is classified as a new customer in the period containing that customer's first valid purchase observed in the dataset.

For each persistent customer identifier:

> **First Purchase Date = MIN(valid purchase timestamp)**

The customer is considered new only in the period containing this first observed purchase.

Because the dataset contains a finite observation window, the metric must be described as **first observed purchase** rather than guaranteed lifetime first purchase.

**Supports:** BR-002, BR-003

---

#### AR-006 — Repeat Customer

**Requirement:**
A repeat customer is a persistent customer identifier that completes a valid purchase after their first observed valid purchase.

Repeat purchasing must be evaluated at customer level and must not be inferred from repeated transaction-specific customer identifiers.

**Supports:** BR-002, BR-003

---

#### AR-007 — Repeat Purchase Rate

**Requirement:**
Repeat Purchase Rate must have an explicitly documented denominator.

The default customer-level definition will be:

> **Repeat Purchase Rate = Customers with more than one valid order / Customers with at least one valid order**

Alternative period-specific definitions may be used only if clearly labeled and documented.

**Supports:** BR-003

---

#### AR-008 — Customer Acquisition Cohort

**Requirement:**
Customer acquisition cohorts must be assigned using the month of each customer's first observed valid purchase.

Example:

> A customer whose first observed purchase occurred in March 2018 belongs to the **2018-03 acquisition cohort**.

Cohort analyses must use persistent customer identifiers and must separate cohort membership from subsequent purchase periods.

**Supports:** BR-003

---

#### AR-009 — Cohort Retention

**Requirement:**
Retention must measure the proportion of customers from an acquisition cohort who return and complete a valid purchase in a subsequent analytical period.

For cohort (c) and period (t):

> **Retention(c,t) = Returning Customers from Cohort c in Period t / Customers Originally in Cohort c**

The project must explicitly state that observed retention is constrained by the dataset's finite historical window.

**Supports:** BR-003

---

#### AR-010 — RFM Customer Segmentation

**Requirement:**
Customer-value segmentation will use Recency, Frequency, and Monetary dimensions.

* **Recency:** time since the customer's most recent valid purchase relative to the analytical reference date;
* **Frequency:** number of valid orders associated with the persistent customer;
* **Monetary:** cumulative GMV associated with the persistent customer.

Customers may be scored into quantiles or another documented scoring framework.

Segment labels such as *Champions*, *Loyal Customers*, or *At Risk* must be derived from transparent rules rather than manually assigned after inspecting results.

**Supports:** BR-004

---

#### AR-011 — Product & Category Performance

**Requirement:**
Product and category performance must be evaluated using measures calculated at the appropriate item-level grain.

Relevant measures may include:

* units/items sold;
* distinct orders;
* GMV;
* average item price;
* customer count;
* seller count;
* freight value;
* delivery performance;
* review outcomes.

Product or category ranking must identify the metric used rather than relying on the ambiguous term **best-selling**.

**Supports:** BR-005

---

#### AR-012 — Seller Performance

**Requirement:**
Seller performance must combine commercial and operational measures rather than rank sellers solely on transaction value.

Relevant measures may include:

* GMV;
* distinct orders;
* items sold;
* customers served;
* average freight characteristics;
* delivery lead time;
* late-delivery rate;
* average review score.

Comparisons must consider minimum-volume thresholds where low transaction counts could make performance measures unreliable.

**Supports:** BR-006

---

#### AR-013 — Delivery Lead Time

**Requirement:**
Customer delivery lead time must be calculated consistently from the order purchase timestamp to the actual customer delivery timestamp.

> **Delivery Lead Time = Actual Customer Delivery Timestamp − Purchase Timestamp**

Where useful, additional operational lead-time measures may be calculated separately, including:

* purchase-to-approval time;
* approval-to-carrier time;
* carrier-to-customer time.

These measures must not be presented interchangeably.

**Supports:** BR-008, BR-011

---

#### AR-014 — Delivery Delay

**Requirement:**
Delivery performance relative to the promised estimate must compare actual and estimated delivery dates.

> **Delivery Delay = Actual Delivery Timestamp − Estimated Delivery Timestamp**

Classification:

* **On Time / Early:** actual delivery date is on or before the estimated delivery date;
* **Late:** actual delivery date occurs after the estimated delivery date.

The number of days early or late should also be preserved as a continuous measure.

**Supports:** BR-008, BR-009, BR-011

---

#### AR-015 — Late Delivery Rate

**Requirement:**
Late Delivery Rate must be calculated only for orders with sufficient actual and estimated delivery information.

> **Late Delivery Rate = Late Delivered Orders / Delivered Orders with Valid Delivery Comparison**

Orders missing the required timestamps must be reported separately rather than automatically included in the denominator.

**Supports:** BR-008, BR-009, BR-011

---

#### AR-016 — Freight Analysis

**Requirement:**
Freight must be evaluated independently from product transaction value.

Relevant measures may include:

* total freight value;
* average freight per order;
* average freight per item;
* freight-to-item-value ratio;
* freight-to-order-GMV ratio.

Ratios must be calculated using compatible grains and must handle zero or missing denominators explicitly.

**Supports:** BR-005, BR-006, BR-007, BR-008

---

#### AR-017 — Review Score Metrics

**Requirement:**
Customer-review performance must preserve the original review-score scale and support metrics such as:

* average review score;
* median review score;
* review-score distribution;
* proportion of low-score reviews;
* proportion of high-score reviews.

The threshold defining **low review** must be documented in the KPI framework rather than assumed implicitly.

**Supports:** BR-010, BR-011

---

#### AR-018 — Delivery & Review Relationship

**Requirement:**
The relationship between delivery performance and customer-review outcomes must be evaluated using both descriptive and inferential methods where appropriate.

Analyses may include:

* review-score distributions for on-time versus late deliveries;
* differences in mean or median review score;
* confidence intervals;
* effect-size measures;
* statistical hypothesis tests;
* regression-based analysis where assumptions are appropriate.

Results must distinguish **statistical association** from **causal effect**.

**Supports:** BR-011

---

#### AR-019 — Time-Series Comparison

**Requirement:**
Performance over time must support consistent month-over-month and, where data coverage permits, year-over-year comparisons.

For percentage-change measures:

> **Growth Rate = (Current Period − Previous Comparable Period) / Previous Comparable Period**

Periods with incomplete source-data coverage must be identified before interpreting growth rates.

**Supports:** BR-001, BR-002

---

#### AR-020 — Geographic Comparisons

**Requirement:**
Geographic performance comparisons must be calculated at a documented geographic level such as state or city.

Relevant measures may include:

* GMV;
* orders;
* customers;
* average order value;
* freight ratios;
* delivery lead time;
* late-delivery rate;
* review score.

Comparisons involving small populations must disclose or filter low-volume geographic groups where necessary to avoid misleading conclusions.

**Supports:** BR-007, BR-008, BR-010

---

#### AR-021 — Metric Grain Validation

**Requirement:**
Every analytical metric must have an explicitly documented natural grain.

Metrics originating from different grains must not be combined through joins without validation against duplication or aggregation errors.

Examples include:

* order-level metrics;
* order-item-level metrics;
* payment-level metrics;
* customer-level metrics;
* seller-level metrics;
* review-level metrics.

Where necessary, measures must be aggregated to a compatible grain before tables are joined.

---

#### AR-022 — Analytical Population Definition

**Requirement:**
Every KPI or analysis must define its analytical population.

The definition should document where relevant:

* included order statuses;
* excluded order statuses;
* required timestamps;
* missing-value handling;
* date-window restrictions;
* minimum sample or volume thresholds;
* unit of analysis.

A metric must not rely on an undocumented global filter.

---

#### AR-023 — No Silent Imputation

**Requirement:**
Missing analytical values must not be automatically replaced with zero, averages, medians, or other imputed values unless an explicit methodological rationale is documented.

Where missingness prevents calculation, the record should normally remain identifiable as unavailable rather than being converted into a valid observed value.

---

#### AR-024 — Reproducible Analytical Logic

**Requirement:**
Business-critical analytical calculations must be implemented through reproducible SQL, dbt, or Python logic rather than manual spreadsheet or dashboard-only calculations whenever practical.

Dashboard calculations may be used for presentation-specific logic, but core metric definitions should originate from governed analytical layers.

---

#### AR-025 — Decision-Oriented Interpretation

**Requirement:**
Analytical outputs must connect observed results to the business questions defined in the Business Case.

The project must distinguish among:

* observation;
* interpretation;
* statistical evidence;
* business implication;
* recommendation.

Recommendations must not claim certainty beyond what the available data and analytical methodology support.

### 6. Non-Functional Requirements

Non-functional requirements define the quality, maintainability, reproducibility, security, and technical operating standards expected from the Executive Commerce Intelligence Platform.

---

#### NFR-001 — Reproducibility

**Requirement:**
The project environment and analytical workflow must be reproducible from documented instructions.

A new user should be able to recreate the core analytical environment using the repository documentation and project configuration.

This includes:

* Python environment setup;
* required dependencies;
* PostgreSQL environment;
* dbt setup;
* source-data placement;
* transformation execution;
* analytical workflow execution.

---

#### NFR-002 — Version Control

**Requirement:**
Project code, documentation, configuration, and analytical logic must be maintained under Git version control.

Changes must be grouped into meaningful commits with descriptive commit messages.

Generated files, local environments, secrets, and raw datasets that do not belong in version control must be excluded through `.gitignore`.

---

#### NFR-003 — Environment Isolation

**Requirement:**
Python dependencies must be isolated from the user's global Python installation through a project-specific virtual environment.

The project must document the Python version used for development.

---

#### NFR-004 — Containerized Database Environment

**Requirement:**
The PostgreSQL analytical database must be capable of running within a Docker-managed environment rather than requiring a manually configured local PostgreSQL installation.

The container configuration should allow the database environment to be recreated consistently.

---

#### NFR-005 — Configuration Management

**Requirement:**
Environment-specific configuration must be separated from business and analytical logic.

Examples include:

* database host;
* database port;
* database name;
* database user;
* credentials;
* file-system paths where appropriate.

Configuration values should not be hard-coded repeatedly throughout analytical scripts.

---

#### NFR-006 — Secret Management

**Requirement:**
Passwords, credentials, API keys, tokens, or other secrets must never be committed to the public repository.

Secrets must be stored through appropriate local environment variables or configuration mechanisms.

The repository may include an example configuration file such as:

`.env.example`

but must never expose real credentials.

---

#### NFR-007 — Modular Project Structure

**Requirement:**
Project components must be organized by responsibility rather than implemented as one large notebook or script.

The repository should maintain clear separation among:

* documentation;
* source data;
* ingestion logic;
* transformations;
* analytical code;
* tests;
* dashboards;
* configuration.

---

#### NFR-008 — Code Readability

**Requirement:**
Python and SQL code must prioritize readability and maintainability.

Code should use:

* descriptive variable and object names;
* consistent formatting;
* comments where they explain non-obvious decisions;
* reusable functions where appropriate;
* modular SQL transformations;
* limited duplication of business logic.

---

#### NFR-009 — Documentation

**Requirement:**
The project must contain sufficient technical and business documentation for another analyst or engineer to understand the solution without relying on undocumented context.

Documentation must include, where applicable:

* business case;
* requirements;
* KPI definitions;
* source-data description;
* data model;
* architecture;
* data-quality rules;
* transformation logic;
* assumptions;
* limitations;
* setup instructions;
* analytical methodology.

---

#### NFR-010 — Data Model Documentation

**Requirement:**
Analytical tables must document:

* purpose;
* grain;
* primary or surrogate key;
* relevant foreign keys;
* source models;
* important fields;
* business logic.

Fact and dimension tables must be clearly distinguishable.

---

#### NFR-011 — Data Quality Testing

**Requirement:**
Critical assumptions about the source and analytical data must be validated through automated or reproducible tests where practical.

Tests may include:

* uniqueness;
* not-null constraints;
* accepted values;
* referential integrity;
* logical timestamp validation;
* non-negative monetary values;
* expected row-grain conditions.

Failures must be visible rather than silently ignored.

---

#### NFR-012 — Transformation Testing

**Requirement:**
Critical transformation logic must include tests appropriate to its implementation.

Where dbt is used, tests should be defined for important models and columns.

Where Python is used for reusable logic, unit tests should be implemented for critical functions where appropriate.

---

#### NFR-013 — Idempotent Data Processing

**Requirement:**
Where practical, data-ingestion and transformation processes should be idempotent.

Running the same pipeline repeatedly against the same source data should not create unintended duplicate records or materially different results.

---

#### NFR-014 — Logging & Error Visibility

**Requirement:**
Data-processing scripts must provide sufficient logging to indicate:

* process start;
* source being processed;
* records processed where useful;
* successful completion;
* relevant warnings;
* failures.

Errors must not be silently suppressed.

---

#### NFR-015 — Maintainable Metric Logic

**Requirement:**
Core business metrics should be defined centrally where practical rather than independently reimplemented in multiple dashboards, notebooks, or scripts.

Changes to metric definitions should require modification in as few places as reasonably possible.

---

#### NFR-016 — Performance Awareness

**Requirement:**
Transformations and analytical queries must be designed with reasonable performance considerations.

The implementation should avoid unnecessary:

* full-table duplication;
* repeated expensive calculations;
* Cartesian joins;
* row-by-row processing where vectorized or set-based operations are appropriate.

Performance optimizations should remain proportional to the scale of the dataset.

---

#### NFR-017 — Analytical Auditability

**Requirement:**
Material analytical conclusions must be traceable to:

* defined business questions;
* governed KPI definitions;
* analytical datasets;
* reproducible SQL or Python logic.

A reviewer should be able to understand how an important result was produced.

---

#### NFR-018 — Repository Quality

**Requirement:**
The public GitHub repository must be organized as a professional portfolio artifact.

It should include:

* a clear README;
* meaningful directory organization;
* architecture and data-model diagrams;
* documented setup instructions;
* selected analytical findings;
* links to external visualizations where applicable;
* clearly stated project limitations.

Temporary, exploratory, or irrelevant files must not clutter the public repository.

---

#### NFR-019 — Continuous Integration

**Requirement:**
The project should use GitHub Actions for automated validation once the relevant code and tests are available.

The CI workflow may include:

* Python tests;
* formatting or linting checks;
* dbt validation;
* selected data-model tests where feasible.

A failing validation should produce a visible failed workflow rather than being ignored.

---

#### NFR-020 — Platform Independence

**Requirement:**
The project should minimize unnecessary dependence on the developer's local Windows configuration.

Where practical, portable technologies such as:

* Docker;
* Python virtual environments;
* environment variables;
* relative project paths;
* documented setup scripts

should be used to improve reproducibility across machines.

---

#### NFR-021 — Data Privacy & Ethical Use

**Requirement:**
The project must preserve the anonymized nature of the source data and must not attempt to infer or reconstruct the identity of real customers.

Public outputs should avoid exposing unnecessary record-level information when aggregated results are sufficient for the analytical purpose.

---

#### NFR-022 — Analytical Transparency

**Requirement:**
The project must explicitly distinguish:

* source facts;
* derived metrics;
* analytical assumptions;
* statistical findings;
* business interpretations;
* recommendations.

Limitations must be communicated alongside conclusions when they materially affect interpretation.

---

### 7. Requirements Traceability

The following matrix provides an initial mapping between business questions and major requirements.

This matrix will evolve as the data model, KPI framework, analytical marts, and dashboard are implemented.

| Business Question                                | Business Requirements  | Key Data Requirements                          | Key Analytical Requirements                    | Planned Analytical Layer             |
| ------------------------------------------------ | ---------------------- | ---------------------------------------------- | ---------------------------------------------- | ------------------------------------ |
| **BQ-01 — Growth Drivers**                       | BR-001, BR-002         | DR-001, DR-003, DR-010, DR-011, DR-012         | AR-001, AR-002, AR-003, AR-019                 | `mart_executive`                     |
| **BQ-02 — Healthy Growth**                       | BR-001, BR-003, BR-010 | DR-001, DR-002, DR-007, DR-008, DR-010         | AR-004, AR-007, AR-015, AR-017, AR-019         | `mart_executive`                     |
| **BQ-03 — New vs Repeat Customers**              | BR-003                 | DR-001, DR-002, DR-010                         | AR-004, AR-005, AR-006, AR-007, AR-008, AR-009 | `mart_customer`                      |
| **BQ-04 — Customer Value**                       | BR-004                 | DR-001, DR-002, DR-003, DR-012                 | AR-004, AR-010                                 | `mart_customer`                      |
| **BQ-05 — Commercial Performance**               | BR-005, BR-006, BR-007 | DR-003, DR-004, DR-005, DR-009, DR-012         | AR-001, AR-011, AR-012, AR-020                 | `mart_commercial`                    |
| **BQ-06 — Commercial vs Operational Trade-offs** | BR-005, BR-006, BR-007 | DR-003, DR-004, DR-005, DR-008, DR-009, DR-012 | AR-011, AR-012, AR-015, AR-016, AR-017, AR-020 | `mart_commercial`, `mart_operations` |
| **BQ-07 — Logistics Bottlenecks**                | BR-006, BR-007, BR-008 | DR-001, DR-005, DR-008, DR-009                 | AR-012, AR-013, AR-014, AR-015, AR-016, AR-020 | `mart_operations`                    |
| **BQ-08 — Delivery Estimate Accuracy**           | BR-009                 | DR-001, DR-008, DR-009                         | AR-014, AR-015, AR-020                         | `mart_operations`                    |
| **BQ-09 — Delivery & Satisfaction**              | BR-010, BR-011         | DR-001, DR-007, DR-008                         | AR-013, AR-014, AR-015, AR-017, AR-018         | `mart_customer_experience`           |
| **BQ-10 — Poor Review Drivers**                  | BR-010, BR-011         | DR-003, DR-004, DR-005, DR-007, DR-008, DR-009 | AR-011, AR-012, AR-017, AR-018, AR-020         | `mart_customer_experience`           |

---

### 8. Requirement Governance

Requirements may evolve as source-data profiling reveals constraints or opportunities that were not visible during initial planning.

Any material requirement change should be:

1. documented;
2. justified;
3. reflected in related KPI or data-model definitions where applicable;
4. implemented through version-controlled changes.

The requirements should therefore be treated as a living specification rather than a fixed document disconnected from implementation.

# 9. Source Validation Status

The initial business, data, analytical, and non-functional requirements were defined before detailed inspection of the source data.

A reproducible source-profiling and data-quality workflow has subsequently been implemented to validate the structural assumptions underlying the requirements.

The profiling process includes:

* table and column profiling;
* missing-value analysis;
* duplicate detection;
* source-key validation;
* referential-integrity validation;
* cardinality analysis;
* dataset-specific profiling;
* timestamp and temporal-consistency validation;
* monetary-value profiling;
* payment reconciliation;
* delivery-quality profiling;
* review-score validation;
* exception-level investigation.

The following section records how the original data requirements were affected by empirical source validation.

---

## 9.1 Data Requirement Validation Summary

| Requirement                                | Validation Status                                         | Key Evidence                                                                                                                                                                                                                          | Implementation Implication                                                                                                                                                                 |
| ------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **DR-001 — Order-Level Transaction Data**  | **Validated with exceptions**                             | 99,441 orders and 99,441 unique `order_id` values confirm one row per order. Eight order statuses are present. Operational timestamps contain some missing values.                                                                    | Preserve order grain and status. KPI populations must define required statuses and timestamps explicitly.                                                                                  |
| **DR-002 — Persistent Customer Identity**  | **Validated**                                             | 99,441 unique `customer_id` values but only 96,096 `customer_unique_id` values. 2,997 persistent identifiers occur in multiple customer records, with a maximum of 17 records for one persistent customer.                            | `customer_unique_id` must be used for repeat purchasing, cohorts, retention, frequency, and RFM analysis.                                                                                  |
| **DR-003 — Order Item Grain**              | **Validated**                                             | 112,650 rows and 112,650 distinct `order_id + order_item_id` combinations.                                                                                                                                                            | The natural source grain is one order-item position. Order-level measures must be aggregated before being combined with this grain.                                                        |
| **DR-004 — Product Attributes**            | **Validated with exceptions**                             | 32,951 unique products. 610 products have no category, 2 products are missing at least one physical attribute, and 2 observed product categories have no English translation.                                                         | Missing and untranslated categories must remain identifiable. Category enrichment must not use an inner join that silently removes products.                                               |
| **DR-005 — Seller Identity**               | **Validated**                                             | 3,095 rows and 3,095 unique `seller_id` values. All seller references from Order Items resolve successfully.                                                                                                                          | Seller-level dimensional modeling can use the validated source identifier as the natural key.                                                                                              |
| **DR-006 — Payment Data**                  | **Validated with multi-row grain**                        | `order_id + payment_sequential` uniquely identifies all 103,886 payment records. 2,961 orders contain multiple payment records, with a maximum of 29 records for one order.                                                           | Payment records must remain at payment-sequence grain or be explicitly aggregated to order grain before joining to other facts.                                                            |
| **DR-007 — Customer Review Data**          | **Validated with multi-row grain**                        | 99,224 review rows. `review_id` alone is not unique, while `review_id + order_id` uniquely identifies the source rows. 547 orders have multiple reviews, with a maximum of 3 reviews per order.                                       | Reviews must not be joined to an order-level model under an assumed one-review-per-order relationship. Review-grain logic must be explicit.                                                |
| **DR-008 — Delivery Performance Data**     | **Validated with data-quality conditions**                | 96,478 orders have status `delivered`. 14 delivered orders lack an approval timestamp, 2 lack a carrier timestamp, and 8 lack the customer-delivery timestamp.                                                                        | Delivery KPIs must define required timestamps and exclude unavailable comparisons from denominators rather than imputing them.                                                             |
| **DR-009 — Geographic Data**               | **Validated with significant transformation requirement** | Geolocation contains 1,000,163 rows but only 19,015 ZIP-code prefixes. 261,831 rows are exact duplicates, 17,972 ZIP prefixes have multiple rows, and one ZIP prefix has up to 1,146 observations.                                    | Raw geolocation must be standardized to a controlled geographic grain before enrichment. Direct joins from customers or sellers to raw geolocation are prohibited for analytical measures. |
| **DR-010 — Calendar & Time Dimensions**    | **Validated**                                             | Order purchase activity spans the historical observation window required for calendar analysis. Source timestamps support derived date attributes.                                                                                    | A reusable date dimension should be generated for consistent period-based analytics.                                                                                                       |
| **DR-011 — Order Status**                  | **Validated**                                             | Eight statuses were observed: `delivered`, `shipped`, `canceled`, `unavailable`, `invoiced`, `processing`, `created`, and `approved`.                                                                                                 | There will be no universal global order-status filter. Analytical populations must be defined per KPI.                                                                                     |
| **DR-012 — Monetary Measures**             | **Validated with reconciliation exceptions**              | No negative values were found in item price, freight value, or payment value. Payment and item-plus-freight totals reconcile within one cent for 99.6929% of comparable orders; 303 orders differ by more than one cent.              | GMV, freight, and payment value must remain separate governed measures. Payment value must not be assumed to equal item value plus freight universally.                                    |
| **DR-013 — Referential Integrity**         | **Validated**                                             | Zero orphan keys were found across Orders → Customers, Order Items → Orders, Order Items → Products, Order Items → Sellers, Payments → Orders, and Reviews → Orders.                                                                  | Core source relationships can be modeled with high confidence while retaining automated referential-integrity tests downstream.                                                            |
| **DR-014 — Duplicate Detection**           | **Validated with source-specific exception**              | No complete duplicate rows were found in the primary transactional sources. Geolocation contains 261,831 duplicate rows beyond the first occurrence.                                                                                  | Deduplication logic must be source-specific and must not be applied globally without understanding expected grain.                                                                         |
| **DR-015 — Missing Data**                  | **Validated as required**                                 | Missingness exists in operational timestamps, product categories, product physical attributes, reviews, and selected child relationships.                                                                                             | Missing values must remain distinct from zero or negative business outcomes and must be handled according to metric-specific rules.                                                        |
| **DR-016 — Data-Type & Domain Validation** | **Validated with continued staging requirements**         | Monetary values are non-negative. All 99,224 observed review scores fall within the valid 1–5 scale. Source timestamps are provided through CSV fields and require explicit datetime conversion downstream.                           | Staging models must enforce target data types, accepted values, and appropriate domain tests.                                                                                              |
| **DR-017 — Temporal Consistency**          | **Validated with exceptions**                             | No approval-before-purchase, customer-delivery-before-purchase, or estimated-delivery-before-purchase violations were found. 1,359 records show carrier handoff before approval and 23 show customer delivery before carrier handoff. | Temporal anomalies must be preserved and flagged rather than silently corrected or removed. Intermediate operational-duration metrics must use valid-sequence populations.                 |
| **DR-018 — Raw Data Preservation**         | **Implemented**                                           | Original CSV files are stored under `data/raw/`, excluded from Git, and are not modified by profiling workflows.                                                                                                                      | Cleaning and business transformations will occur only in downstream layers.                                                                                                                |
| **DR-019 — Source Traceability**           | **Implemented in profiling layer**                        | Profiling code and generated reports are version-controlled and reproduce structural, quality, and exception findings.                                                                                                                | Future warehouse and dbt models should extend this lineage from source through marts and KPIs.                                                                                             |
| **DR-020 — Data Privacy**                  | **Maintained**                                            | The project uses the anonymized source identifiers and does not attempt to reconstruct customer identities.                                                                                                                           | Customer-level modeling will continue to use anonymous analytical identifiers only.                                                                                                        |

---

## 9.2 Validated Source Grains

Source profiling confirmed the following grains:

| Source               | Validated Grain                                                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| Customers            | One row per `customer_id`                                                                       |
| Orders               | One row per `order_id`                                                                          |
| Order Items          | One row per `order_id + order_item_id`                                                          |
| Payments             | One row per `order_id + payment_sequential`                                                     |
| Reviews              | One row per `review_id + order_id`                                                              |
| Products             | One row per `product_id`                                                                        |
| Sellers              | One row per `seller_id`                                                                         |
| Category Translation | One row per `product_category_name`                                                             |
| Geolocation          | Multiple observations per ZIP-code prefix; analytical grain requires downstream standardization |

These grains will guide fact-table design, staging transformations, and join strategies.

---

## 9.3 Validated Core Referential Integrity

The following source relationships achieved 100% referential coverage during profiling:

* Orders → Customers through `customer_id`;
* Order Items → Orders through `order_id`;
* Order Items → Products through `product_id`;
* Order Items → Sellers through `seller_id`;
* Payments → Orders through `order_id`;
* Reviews → Orders through `order_id`.

No orphan foreign-key values were found in these relationships.

This validation confirms structural consistency but does not eliminate the need for downstream automated referential-integrity tests.

---

## 9.4 Analytical Population Implications

Source validation confirms that the platform should not rely on a single universal definition of a **valid order**.

Different analytical questions require different eligible populations.

### Commercial Population

Commercial measures such as GMV and Items Sold should originate from eligible order-item records.

Order status treatment must be explicitly documented in the KPI framework.

### Customer Lifecycle Population

Customer acquisition, repeat purchasing, cohorts, and RFM must use `customer_unique_id` and a documented valid-purchase population.

### Delivery Population

Delivery metrics should primarily use delivered orders with the timestamps required by each calculation.

Orders missing required timestamps must remain measurable as unavailable comparisons rather than being silently imputed.

### Customer Experience Population

Review KPIs should use valid observed review records.

An order without a review represents **no observed review**, not a review score of zero.

### Payment Population

Payment measures should originate from payment records and be aggregated to an appropriate grain before being combined with order or item measures.

Payment value, GMV, and freight must remain conceptually distinct measures.

---

## 9.5 Data Quality Treatment Principles

The profiling results establish the following implementation principles:

1. source anomalies will be preserved in raw and staging layers;
2. invalid or questionable records will be flagged rather than silently deleted;
3. metric-specific populations will be defined in governed analytical models;
4. one-to-many relationships will be aggregated to compatible grains before analytical joins;
5. monetary reconciliation will use integer-cent logic rather than floating-point equality;
6. missing values will remain distinct from valid zero values;
7. source geolocation will be standardized before customer or seller enrichment;
8. review multiplicity will be explicitly handled before producing order-level customer-experience metrics;
9. temporal-duration metrics will use appropriate sequence-validity rules;
10. all material exclusions must be documented and reproducible.

---

## 9.6 Validation Evidence

The validation findings are generated through version-controlled profiling workflows located under:

`src/profiling/`

The generated evidence is stored under:

`reports/profiling/`

including detailed exception-level reports where source records require additional investigation.

These reports provide the empirical foundation for subsequent KPI validation, staging rules, dimensional modeling, and analytical mart design.
