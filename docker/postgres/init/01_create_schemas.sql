-- Create the governed physical warehouse schemas.
-- RAW is populated by the Python ingestion pipeline.
-- All downstream analytical schemas are managed through dbt transformations.

CREATE SCHEMA IF NOT EXISTS raw;

CREATE SCHEMA IF NOT EXISTS staging;

CREATE SCHEMA IF NOT EXISTS core;

CREATE SCHEMA IF NOT EXISTS intermediate;

CREATE SCHEMA IF NOT EXISTS marts;


-- Document each schema directly inside PostgreSQL.

COMMENT ON SCHEMA raw IS
    'Source-preserving tables loaded by the Python ingestion pipeline.';

COMMENT ON SCHEMA staging IS
    'Typed and standardized source models managed by dbt.';

COMMENT ON SCHEMA core IS
    'Governed dimensional warehouse containing conformed dimensions and atomic facts.';

COMMENT ON SCHEMA intermediate IS
    'Reusable grain-reconciled transformations and governed business logic.';

COMMENT ON SCHEMA marts IS
    'Business-facing KPI-ready analytical datasets.';