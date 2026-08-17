# Business Case

## Executive Commerce Intelligence Platform

### 1. Business Context

This project simulates an analytics engagement for a Brazilian multi-seller e-commerce marketplace using the Brazilian E-Commerce Public Dataset by Olist.

The marketplace connects customers, sellers, products, payments, and logistics operations across Brazil. As transaction volume grows, management requires a reliable analytical foundation to evaluate commercial performance, customer behavior, marketplace operations, and customer experience.

Operational data is distributed across multiple entities, including orders, customers, order items, products, sellers, payments, deliveries, and customer reviews. While these datasets support transactional processes, they are not structured for efficient executive reporting or cross-functional analytics.

The company therefore requires a consolidated analytics platform capable of transforming raw operational data into governed business metrics, dimensional data models, analytical data marts, and decision-oriented insights.

### 2. Problem Statement

The marketplace has access to detailed transactional and operational data, but lacks a unified analytical layer that enables management to consistently evaluate business performance across customers, products, sellers, geography, logistics, and customer experience.

Without standardized metrics and integrated data models, answering cross-functional questions requires repeated ad-hoc analysis and increases the risk of inconsistent definitions, duplicated logic, and conflicting business conclusions.

The core business problem is therefore:

> **How can the marketplace transform fragmented operational data into a reliable decision-support system that helps management understand the drivers of growth, customer retention, commercial performance, and operational efficiency?**

### 3. Project Objective

The objective of the Executive Commerce Intelligence Platform is to design and implement an end-to-end analytics solution that converts raw marketplace data into trustworthy, reusable, and decision-oriented information.

The platform will:

- establish standardized business definitions and KPIs;
- integrate multiple operational data sources into a consistent analytical model;
- implement dimensional data modeling for scalable reporting;
- create reusable analytical data marts for commercial, customer, and operational analysis;
- evaluate customer behavior, retention, product performance, seller performance, and logistics efficiency;
- quantify relationships between operational performance and customer experience;
- provide executive dashboards and analytical insights that support business decision-making;
- document data assumptions, quality rules, analytical limitations, and technical decisions.

### 4. Stakeholders

The Executive Commerce Intelligence Platform is designed to support multiple business functions. Each stakeholder group has different analytical needs and decision responsibilities.

| Stakeholder                             | Primary Interests                                                                  | Decisions Supported                                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Executive Management**                | Business growth, customer health, marketplace performance, operational efficiency  | Identify major performance trends, prioritize strategic initiatives, and allocate resources                       |
| **Finance**                             | GMV, order value, payment behavior, freight costs, revenue quality                 | Monitor commercial performance, assess cost-to-serve, and identify financially inefficient segments               |
| **Commercial / Marketplace Management** | Product categories, sellers, geographic performance, sales mix                     | Identify high-performing categories and sellers, detect underperformance, and prioritize commercial opportunities |
| **Customer / Growth Team**              | Customer acquisition, repeat purchases, retention, customer value                  | Identify valuable customer segments, measure repeat behavior, and support retention strategies                    |
| **Operations & Logistics**              | Delivery lead times, delays, freight performance, geographic bottlenecks           | Identify operational inefficiencies and prioritize areas requiring logistics improvements                         |
| **Customer Experience**                 | Review scores, low-rating incidence, delivery-related dissatisfaction              | Understand the drivers of poor customer experience and identify service improvement opportunities                 |
| **Data & Analytics Team**               | Metric consistency, data quality, reusable models, lineage, analytical scalability | Maintain trusted analytical datasets and ensure that business teams use consistent definitions                    |

#### Stakeholder Decision Framework

The platform is not intended solely to provide descriptive reporting. Its analytical outputs should help stakeholders answer decision-oriented questions such as:

* **Executive Management:** Where is marketplace growth coming from, and is that growth sustainable?
* **Finance:** Which segments generate strong transaction volume but disproportionately high logistics costs?
* **Commercial:** Which categories, sellers, and regions should receive greater commercial attention?
* **Customer / Growth:** Is business growth primarily driven by customer acquisition or by repeat purchasing?
* **Operations:** Where do delivery delays and logistics inefficiencies occur most frequently?
* **Customer Experience:** Which operational factors are most strongly associated with negative customer reviews?
* **Data & Analytics:** Are business metrics consistently defined and reusable across analytical use cases?

### 5. Business Questions

The analytical platform will be designed to answer a set of decision-oriented business questions across commercial performance, customers, marketplace operations, and customer experience.

#### 5.1 Executive Performance

**BQ-01 — What are the primary drivers of marketplace growth over time?**

The analysis should determine whether changes in marketplace performance are primarily associated with order volume, average order value, customer acquisition, repeat purchasing, product mix, or geographic expansion.

**BQ-02 — Is marketplace growth accompanied by healthy customer and operational performance?**

Revenue growth should be evaluated alongside customer retention, delivery performance, logistics costs, and customer satisfaction to distinguish sustainable growth from growth associated with deteriorating operational or customer outcomes.

#### 5.2 Customer Analytics

**BQ-03 — Is business growth primarily driven by new customers or repeat purchasing?**

The analysis should quantify customer acquisition, repeat purchase behavior, purchase frequency, and retention across acquisition cohorts.

**BQ-04 — Which customer segments contribute the greatest economic value to the marketplace?**

Customers should be evaluated using behavioral and monetary characteristics such as recency, frequency, order value, and cumulative purchasing activity.

#### 5.3 Commercial & Marketplace Performance

**BQ-05 — Which product categories, sellers, and geographic markets are the strongest contributors to marketplace performance?**

Performance should be evaluated across transaction volume, GMV, average order value, customer demand, and operational outcomes.

**BQ-06 — Are there high-volume commercial segments associated with disproportionately high logistics costs or poor customer experience?**

The analysis should identify categories, sellers, or geographic regions where strong commercial performance may be offset by freight costs, delivery delays, or negative customer reviews.

#### 5.4 Operations & Logistics

**BQ-07 — Where are the main delivery and logistics bottlenecks in the marketplace?**

Delivery lead times, late-delivery rates, freight costs, geographic patterns, and seller performance should be evaluated to identify recurring operational inefficiencies.

**BQ-08 — How accurately do estimated delivery dates reflect actual delivery performance?**

The analysis should evaluate the magnitude and distribution of delivery estimation errors across regions, categories, sellers, and time periods.

#### 5.5 Customer Experience

**BQ-09 — How strongly is delivery performance associated with customer satisfaction?**

The relationship between delivery delays, delivery lead times, and review scores should be quantified using descriptive and statistical analysis.

**BQ-10 — What characteristics are most commonly associated with poor customer reviews?**

The analysis should investigate whether low review scores are associated with operational, commercial, geographic, or order-level characteristics.

#### Analytical Principle

These questions are intended to guide decision-making rather than produce isolated descriptive statistics. Each question will therefore be mapped to defined KPIs, analytical datasets, transformations, analyses, and dashboard components throughout the project.

### 6. Project Scope

The Executive Commerce Intelligence Platform will cover the design and implementation of an end-to-end analytical solution using marketplace transactional and operational data.

The project scope includes:

#### Data Foundation

* ingestion of the available source datasets into a structured analytical environment;
* profiling and validation of source data;
* definition of data quality rules and validation checks;
* documentation of source entities, relationships, and relevant business definitions.

#### Data Modeling & Analytics Engineering

* design of a dimensional data model using fact and dimension tables;
* implementation of staging, intermediate, warehouse, and analytical mart layers;
* definition of table grain, keys, relationships, and transformation logic;
* development of reusable transformations and standardized business metrics;
* implementation of automated data tests where appropriate.

#### Business Analytics

* executive marketplace performance analysis;
* customer acquisition, repeat purchasing, cohort, and segmentation analysis;
* product-category and seller performance analysis;
* geographic performance analysis;
* logistics and delivery performance analysis;
* customer experience and review analysis;
* evaluation of relationships between operational performance and customer satisfaction.

#### Business Intelligence

* creation of decision-oriented analytical data marts;
* development of an executive Tableau dashboard;
* visualization of commercial, customer, operational, and customer-experience KPIs;
* production of management-oriented analytical conclusions and recommendations.

#### Technical & Analytical Documentation

* business requirements;
* KPI definitions;
* data model documentation;
* architecture documentation;
* data quality rules;
* assumptions and limitations;
* analytical methodology;
* architecture decision records;
* reproducibility instructions.

---

### 7. Out of Scope

The following items are deliberately excluded from the initial project scope:

* real-time or streaming data processing;
* production-grade cloud infrastructure;
* customer acquisition cost, marketing attribution, or advertising ROI analysis where reliable marketing-spend data is unavailable;
* true accounting revenue, gross margin, contribution margin, or profitability calculations where the source data does not provide the required cost and accounting information;
* causal claims that cannot be supported by the observational nature of the available data;
* production deployment of predictive machine-learning models;
* recommendation systems or personalized product ranking;
* fraud detection;
* inventory optimization;
* external market or competitor analysis;
* personally identifiable customer-level profiling.

These capabilities may represent potential extensions but are not required to satisfy the objectives of the current analytics platform.

---

### 8. Success Criteria

The project will be considered successful if it produces a reliable and reproducible analytical foundation capable of supporting the defined business questions.

Success will be evaluated across five dimensions.

#### 8.1 Data Reliability

* critical source datasets are successfully integrated;
* primary and foreign-key relationships are validated where applicable;
* relevant missing values, duplicates, invalid records, and inconsistencies are documented;
* defined data quality tests can be executed reproducibly.

#### 8.2 Analytical Consistency

* core KPIs have explicit business definitions and calculation rules;
* the same metric produces consistent results across analyses and dashboards;
* analytical datasets have clearly documented grain and transformation logic.

#### 8.3 Business Coverage

* each priority business question (BQ-01 to BQ-10) is supported by one or more analytical outputs;
* executive, customer, commercial, operational, and customer-experience perspectives are represented;
* analyses produce decision-oriented conclusions rather than isolated descriptive statistics.

#### 8.4 Technical Reproducibility

* the analytical environment can be recreated from documented instructions;
* transformation logic is version-controlled;
* the warehouse and analytical marts can be rebuilt from the documented source data;
* project dependencies and technical assumptions are documented.

#### 8.5 Decision Support

* the executive dashboard communicates the most relevant KPIs clearly;
* major business findings can be traced back to defined metrics and analytical logic;
* recommendations explicitly connect analytical findings to potential management actions.

---

### 9. Constraints & Assumptions

The analysis is subject to several constraints associated with the available public dataset and the simulated nature of the business engagement.

#### 9.1 Historical Data

The dataset represents a historical observation period and should not be interpreted as reflecting the current performance of Olist or the current Brazilian e-commerce market.

#### 9.2 Simulated Business Engagement

The project is an independent portfolio case study based on publicly available data. Business context, stakeholder needs, and analytical requirements are simulated for educational and portfolio purposes and do not represent internal Olist processes or management decisions.

#### 9.3 Revenue Interpretation

Order and item values will be treated as marketplace transaction value for analytical purposes. They should not automatically be interpreted as accounting revenue, net revenue, or profit.

Where appropriate, the project will use the term **Gross Merchandise Value (GMV)** rather than revenue to avoid overstating what the source data supports.

#### 9.4 Profitability Limitations

The available dataset does not contain a complete view of:

* cost of goods sold;
* seller commissions;
* payment-processing costs;
* marketing spend;
* customer acquisition cost;
* warehousing costs;
* operational overhead;
* taxes;
* marketplace take rate.

Therefore, profitability and contribution-margin conclusions cannot be calculated reliably.

#### 9.5 Customer Identity

Customer-level behavioral analysis will rely on the identifiers available in the source data. The distinction between transactional customer identifiers and persistent customer identifiers must be respected when calculating repeat purchase and retention metrics.

#### 9.6 Observational Data

Relationships identified in the data should generally be interpreted as associations rather than causal effects unless a valid causal methodology and appropriate assumptions can be established.

For example, an association between delivery delays and lower review scores does not by itself prove that the delay caused the lower rating.

#### 9.7 Missing Business Context

Certain organizational policies, operational constraints, seller agreements, service-level agreements, and internal business definitions are unavailable. Where assumptions are necessary, they will be explicitly documented.

#### 9.8 Data Quality

Source data may contain missing values, inconsistent timestamps, duplicates, incomplete relationships, or other quality issues. Records will not be silently removed or corrected without documented analytical justification.

---

### 10. Expected Business Value

The Executive Commerce Intelligence Platform is intended to demonstrate how fragmented marketplace data can be transformed into a consistent analytical system for cross-functional decision support.

The expected value of the platform includes:

#### Improved Executive Visibility

Management receives a consolidated view of marketplace growth, customer behavior, commercial performance, logistics, and customer experience rather than relying on disconnected analyses.

#### Consistent Decision Metrics

Standardized KPI definitions reduce the risk of different teams calculating the same metric differently and reaching conflicting conclusions.

#### Faster Analytical Access

Reusable dimensional models and analytical marts reduce repeated ad-hoc data preparation and allow analysts to focus more heavily on interpretation and decision support.

#### Customer Intelligence

Customer acquisition, repeat behavior, cohorts, and segmentation provide a stronger understanding of marketplace customer dynamics.

#### Commercial Prioritization

Product, seller, and geographic performance analysis helps identify areas of strength, underperformance, and potential commercial opportunity.

#### Operational Improvement

Delivery and logistics analytics help identify recurring bottlenecks, inefficient segments, and areas where operational performance may negatively affect the customer experience.

#### Stronger Data Governance

Documented metric definitions, quality checks, data models, transformation logic, and assumptions create a more transparent and auditable analytical environment.

#### Scalable Analytical Foundation

The architecture establishes reusable analytical components that could support future capabilities such as forecasting, machine learning, experimentation, recommendation systems, or cloud-scale data processing.
