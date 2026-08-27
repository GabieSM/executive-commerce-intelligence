from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

# Resolve the absolute location of this Python script.
# Example:
# <project_root>/src/profiling/profile_sources.py
CURRENT_FILE = Path(__file__).resolve()

# Move two directory levels up from this file:
# profile_sources.py -> profiling -> src -> project root
#
# This makes the script portable because no user-specific absolute
# path is hard-coded in the project.
PROJECT_ROOT = CURRENT_FILE.parents[2]

# Folder containing the original source CSV files.
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Folder where generated profiling reports will be stored.
REPORT_DIR = PROJECT_ROOT / "reports" / "profiling"


# ---------------------------------------------------------------------------
# Source file configuration
# ---------------------------------------------------------------------------

# Map an internal source name to each raw CSV filename.
# Centralizing filenames avoids repeating them throughout the code.
SOURCE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


# ---------------------------------------------------------------------------
# Expected source keys
# ---------------------------------------------------------------------------

# Define the columns expected to uniquely identify records in each
# source where a reliable natural or composite key is available.
#
# The profiling pipeline tests these hypotheses instead of assuming
# that the keys are valid.
EXPECTED_KEYS = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "payments": ["order_id", "payment_sequential"],
    "reviews": ["review_id", "order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "category_translation": ["product_category_name"],
}


# ---------------------------------------------------------------------------
# Expected source relationships
# ---------------------------------------------------------------------------

# Define the principal child-to-parent relationships in the source data.
# These relationships are used to test referential integrity.
SOURCE_RELATIONSHIPS = [
    {
        "relationship_name": "orders_to_customers",
        "child_source": "orders",
        "child_column": "customer_id",
        "parent_source": "customers",
        "parent_column": "customer_id",
    },
    {
        "relationship_name": "order_items_to_orders",
        "child_source": "order_items",
        "child_column": "order_id",
        "parent_source": "orders",
        "parent_column": "order_id",
    },
    {
        "relationship_name": "order_items_to_products",
        "child_source": "order_items",
        "child_column": "product_id",
        "parent_source": "products",
        "parent_column": "product_id",
    },
    {
        "relationship_name": "order_items_to_sellers",
        "child_source": "order_items",
        "child_column": "seller_id",
        "parent_source": "sellers",
        "parent_column": "seller_id",
    },
    {
        "relationship_name": "payments_to_orders",
        "child_source": "payments",
        "child_column": "order_id",
        "parent_source": "orders",
        "parent_column": "order_id",
    },
    {
        "relationship_name": "reviews_to_orders",
        "child_source": "reviews",
        "child_column": "order_id",
        "parent_source": "orders",
        "parent_column": "order_id",
    },
]


def profile_source(
    source_name: str,
    file_name: str,
) -> tuple[dict, list[dict]]:
    """
    Profile one raw CSV source.

    The function produces:

    1. Table-level profiling
       - row count;
       - column count;
       - fully duplicated rows.

    2. Column-level profiling
       - inferred pandas data type;
       - missing-value count;
       - missing-value percentage;
       - distinct-value count;
       - cardinality percentage.

    Returns
    -------
    tuple[dict, list[dict]]
        Table-level result and column-level results.
    """

    # Build the complete path to the raw source file.
    file_path = RAW_DATA_DIR / file_name

    # Stop execution if an expected source file is missing.
    # Silent partial profiling would produce misleading results.
    if not file_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    print(f"Profiling {source_name}: {file_name}")

    # Read the complete source because structural and column profiling
    # requires access to every column.
    df = pd.read_csv(
        file_path,
        low_memory=False,
    )

    # Store the row count once because it is reused below.
    row_count = len(df)

    # Count exact duplicate rows across every column.
    # The first occurrence is retained as the original record.
    duplicate_row_count = df.duplicated(
        keep="first"
    ).sum()

    table_profile = {
        "source_name": source_name,
        "file_name": file_name,
        "row_count": row_count,
        "column_count": len(df.columns),
        "duplicate_row_count": int(duplicate_row_count),
    }

    column_profiles = []

    # Profile every source column independently.
    for column_name in df.columns:

        series = df[column_name]

        # Count missing observations.
        null_count = series.isna().sum()

        # Express missingness as a percentage of the source rows.
        null_percentage = (
            (null_count / row_count) * 100
            if row_count > 0
            else 0.0
        )

        # Count distinct non-null observed values.
        distinct_count = series.nunique(
            dropna=True
        )

        # Cardinality indicates how close the column is to being unique.
        #
        # Example:
        # 99,441 distinct values / 99,441 rows = 100%
        cardinality_percentage = (
            (distinct_count / row_count) * 100
            if row_count > 0
            else 0.0
        )

        column_profiles.append(
            {
                "source_name": source_name,
                "column_name": column_name,
                "data_type": str(series.dtype),
                "null_count": int(null_count),
                "null_percentage": round(
                    null_percentage,
                    4,
                ),
                "distinct_count": int(distinct_count),
                "cardinality_percentage": round(
                    cardinality_percentage,
                    4,
                ),
            }
        )

    return table_profile, column_profiles


def run_profiling() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run structural and column profiling for every raw source.
    """

    table_profiles = []
    column_profiles = []

    # Process sources sequentially so all nine complete DataFrames
    # do not need to remain in memory simultaneously.
    for source_name, file_name in SOURCE_FILES.items():

        table_profile, source_column_profiles = profile_source(
            source_name=source_name,
            file_name=file_name,
        )

        table_profiles.append(table_profile)
        column_profiles.extend(source_column_profiles)

    return (
        pd.DataFrame(table_profiles),
        pd.DataFrame(column_profiles),
    )


def load_source_columns(
    source_name: str,
    columns: list[str],
) -> pd.DataFrame:
    """
    Load only selected columns from a raw source.

    This reduces unnecessary memory usage during validations that
    require only identifiers or a small subset of fields.
    """

    file_name = SOURCE_FILES[source_name]
    file_path = RAW_DATA_DIR / file_name

    return pd.read_csv(
        file_path,
        usecols=columns,
        low_memory=False,
    )


def validate_source_keys() -> pd.DataFrame:
    """
    Validate expected natural and composite source keys.

    A key is considered valid when:
    - no component of the key is missing;
    - no duplicate key combination exists.
    """

    key_profiles = []

    for source_name, key_columns in EXPECTED_KEYS.items():

        df = load_source_columns(
            source_name=source_name,
            columns=key_columns,
        )

        # Count rows containing a null in any key component.
        null_key_count = (
            df[key_columns]
            .isna()
            .any(axis=1)
            .sum()
        )

        # Mark every row participating in a duplicated key combination.
        duplicate_key_mask = df.duplicated(
            subset=key_columns,
            keep=False,
        )

        duplicate_key_row_count = duplicate_key_mask.sum()

        # Count unique key combinations.
        distinct_key_count = (
            df[key_columns]
            .drop_duplicates()
            .shape[0]
        )

        key_is_valid = (
            null_key_count == 0
            and duplicate_key_row_count == 0
        )

        key_profiles.append(
            {
                "source_name": source_name,
                "key_columns": " + ".join(key_columns),
                "row_count": len(df),
                "distinct_key_count": distinct_key_count,
                "null_key_count": int(null_key_count),
                "duplicate_key_row_count": int(
                    duplicate_key_row_count
                ),
                "key_is_valid": bool(key_is_valid),
            }
        )

    return pd.DataFrame(key_profiles)


def validate_source_relationships() -> pd.DataFrame:
    """
    Validate referential integrity across configured source relationships.

    A foreign-key value is considered an orphan when it exists in the
    child table but cannot be found in the referenced parent table.
    """

    relationship_profiles = []

    for relationship in SOURCE_RELATIONSHIPS:

        child_source = relationship["child_source"]
        child_column = relationship["child_column"]

        parent_source = relationship["parent_source"]
        parent_column = relationship["parent_column"]

        child_df = load_source_columns(
            source_name=child_source,
            columns=[child_column],
        )

        parent_df = load_source_columns(
            source_name=parent_source,
            columns=[parent_column],
        )

        # Build a set of valid parent values for efficient lookup.
        parent_keys = set(
            parent_df[parent_column]
            .dropna()
            .unique()
        )

        # A child value is orphaned when it is non-null but missing
        # from the referenced parent key set.
        orphan_mask = (
            child_df[child_column].notna()
            & ~child_df[child_column].isin(parent_keys)
        )

        orphan_row_count = orphan_mask.sum()

        orphan_key_count = (
            child_df.loc[
                orphan_mask,
                child_column,
            ]
            .nunique()
        )

        non_null_child_count = (
            child_df[child_column]
            .notna()
            .sum()
        )

        # Coverage represents the percentage of foreign-key rows that
        # successfully resolve to a parent record.
        relationship_coverage_percentage = (
            (
                (non_null_child_count - orphan_row_count)
                / non_null_child_count
            )
            * 100
            if non_null_child_count > 0
            else 100.0
        )

        relationship_profiles.append(
            {
                "relationship_name":
                    relationship["relationship_name"],
                "child_source": child_source,
                "child_column": child_column,
                "parent_source": parent_source,
                "parent_column": parent_column,
                "child_row_count": len(child_df),
                "orphan_row_count": int(orphan_row_count),
                "orphan_key_count": int(orphan_key_count),
                "coverage_percentage": round(
                    relationship_coverage_percentage,
                    4,
                ),
                "relationship_is_valid":
                    orphan_row_count == 0,
            }
        )

    return pd.DataFrame(relationship_profiles)


def run_dataset_specific_profiling(
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run profiling checks that are specific to the Olist source model.

    These checks investigate business-relevant cardinalities and data
    conditions that generic table/column profiling cannot fully explain.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Dataset-specific metrics and order-status distribution.
    """

    dataset_metrics = []

    def add_metric(
        domain: str,
        metric_name: str,
        metric_value,
        interpretation: str,
    ) -> None:
        """
        Add one standardized result to the dataset-specific report.
        """

        dataset_metrics.append(
            {
                "domain": domain,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "interpretation": interpretation,
            }
        )

    # ------------------------------------------------------------------
    # Customer identity
    # ------------------------------------------------------------------

    customers = load_source_columns(
        source_name="customers",
        columns=[
            "customer_id",
            "customer_unique_id",
        ],
    )

    # customer_id is the transactional identifier used by Orders.
    distinct_customer_ids = customers[
        "customer_id"
    ].nunique()

    # customer_unique_id is intended to identify a persistent customer
    # across potentially multiple transactional customer records.
    distinct_unique_customers = customers[
        "customer_unique_id"
    ].nunique()

    customer_record_counts = customers[
        "customer_unique_id"
    ].value_counts()

    persistent_ids_with_multiple_records = (
        customer_record_counts > 1
    ).sum()

    max_records_per_persistent_customer = (
        customer_record_counts.max()
    )

    add_metric(
        "customers",
        "distinct_customer_id",
        int(distinct_customer_ids),
        "Transactional customer identifiers.",
    )

    add_metric(
        "customers",
        "distinct_customer_unique_id",
        int(distinct_unique_customers),
        "Persistent customer identifiers.",
    )

    add_metric(
        "customers",
        "persistent_ids_with_multiple_records",
        int(persistent_ids_with_multiple_records),
        "Persistent customers represented by more than one customer_id.",
    )

    add_metric(
        "customers",
        "max_records_per_persistent_customer",
        int(max_records_per_persistent_customer),
        "Maximum customer records linked to one customer_unique_id.",
    )

    # ------------------------------------------------------------------
    # Orders and order-status behavior
    # ------------------------------------------------------------------

    orders = load_source_columns(
        source_name="orders",
        columns=[
            "order_id",
            "order_status",
        ],
    )

    # Produce a dedicated distribution table because order status is
    # central to defining future KPI analytical populations.
    order_status_distribution = (
        orders["order_status"]
        .value_counts(dropna=False)
        .rename_axis("order_status")
        .reset_index(name="order_count")
    )

    order_status_distribution[
        "percentage"
    ] = (
        order_status_distribution["order_count"]
        / len(orders)
        * 100
    ).round(4)

    # ------------------------------------------------------------------
    # Orders without related item/payment/review records
    # ------------------------------------------------------------------

    child_sources = {
        "order_items": "items",
        "payments": "payments",
        "reviews": "reviews",
    }

    for source_name, label in child_sources.items():

        child_orders = load_source_columns(
            source_name=source_name,
            columns=["order_id"],
        )

        # Identify parent orders that have no record in the child source.
        missing_child_count = (
            ~orders["order_id"].isin(
                child_orders["order_id"]
            )
        ).sum()

        add_metric(
            "orders",
            f"orders_without_{label}",
            int(missing_child_count),
            (
                f"Orders with no corresponding record "
                f"in the {source_name} source."
            ),
        )

    # ------------------------------------------------------------------
    # Payment multiplicity
    # ------------------------------------------------------------------

    payments = load_source_columns(
        source_name="payments",
        columns=[
            "order_id",
            "payment_sequential",
        ],
    )

    payments_per_order = payments[
        "order_id"
    ].value_counts()

    orders_with_multiple_payments = (
        payments_per_order > 1
    ).sum()

    max_payments_per_order = payments_per_order.max()

    add_metric(
        "payments",
        "orders_with_multiple_payment_records",
        int(orders_with_multiple_payments),
        "Orders represented by more than one payment record.",
    )

    add_metric(
        "payments",
        "max_payment_records_per_order",
        int(max_payments_per_order),
        "Maximum observed payment records associated with one order.",
    )

    # ------------------------------------------------------------------
    # Review multiplicity and review-key behavior
    # ------------------------------------------------------------------

    reviews = load_source_columns(
        source_name="reviews",
        columns=[
            "review_id",
            "order_id",
        ],
    )

    reviews_per_order = reviews[
        "order_id"
    ].value_counts()

    orders_with_multiple_reviews = (
        reviews_per_order > 1
    ).sum()

    max_reviews_per_order = reviews_per_order.max()

    distinct_review_ids = reviews[
        "review_id"
    ].nunique()

    duplicated_review_ids = (
        reviews["review_id"]
        .value_counts()
        .gt(1)
        .sum()
    )

    add_metric(
        "reviews",
        "distinct_review_id",
        int(distinct_review_ids),
        "Distinct review identifiers observed in the review source.",
    )

    add_metric(
        "reviews",
        "duplicated_review_ids",
        int(duplicated_review_ids),
        (
            "Review identifiers appearing in more than one source row; "
            "review_id alone is therefore not a unique row key."
        ),
    )

    add_metric(
        "reviews",
        "orders_with_multiple_reviews",
        int(orders_with_multiple_reviews),
        "Orders associated with more than one review record.",
    )

    add_metric(
        "reviews",
        "max_reviews_per_order",
        int(max_reviews_per_order),
        "Maximum review records associated with one order.",
    )

    # ------------------------------------------------------------------
    # Product completeness and translation coverage
    # ------------------------------------------------------------------

    products = load_source_columns(
        source_name="products",
        columns=[
            "product_id",
            "product_category_name",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
    )

    translations = load_source_columns(
        source_name="category_translation",
        columns=["product_category_name"],
    )

    products_missing_category = products[
        "product_category_name"
    ].isna().sum()

    physical_columns = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    # Count products missing at least one physical attribute.
    products_missing_physical_attributes = (
        products[physical_columns]
        .isna()
        .any(axis=1)
        .sum()
    )

    product_categories = set(
        products["product_category_name"]
        .dropna()
        .unique()
    )

    translated_categories = set(
        translations["product_category_name"]
        .dropna()
        .unique()
    )

    # Set difference identifies product categories that are used
    # in Products but absent from the translation reference.
    untranslated_categories = sorted(
        product_categories - translated_categories
    )

    add_metric(
        "products",
        "products_missing_category",
        int(products_missing_category),
        "Products without a source product category.",
    )

    add_metric(
        "products",
        "products_missing_physical_attributes",
        int(products_missing_physical_attributes),
        "Products missing at least one weight or dimension field.",
    )

    add_metric(
        "products",
        "distinct_product_categories",
        len(product_categories),
        "Non-null Portuguese categories observed in Products.",
    )

    add_metric(
        "products",
        "categories_without_translation",
        len(untranslated_categories),
        (
            "Categories used by Products but absent from the "
            "English translation reference."
        ),
    )

    add_metric(
        "products",
        "untranslated_category_names",
        " | ".join(untranslated_categories),
        "Names of product categories without translation coverage.",
    )

    # ------------------------------------------------------------------
    # Geolocation multiplicity
    # ------------------------------------------------------------------

    geolocation = load_source_columns(
        source_name="geolocation",
        columns=[
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ],
    )

    distinct_zip_prefixes = geolocation[
        "geolocation_zip_code_prefix"
    ].nunique()

    duplicate_geolocation_rows = (
        geolocation.duplicated(
            keep="first"
        ).sum()
    )

    rows_per_zip = geolocation[
        "geolocation_zip_code_prefix"
    ].value_counts()

    zip_prefixes_with_multiple_rows = (
        rows_per_zip > 1
    ).sum()

    max_rows_per_zip_prefix = rows_per_zip.max()

    add_metric(
        "geolocation",
        "distinct_zip_prefixes",
        int(distinct_zip_prefixes),
        "Distinct ZIP-code prefixes represented in geolocation.",
    )

    add_metric(
        "geolocation",
        "duplicate_rows_after_first",
        int(duplicate_geolocation_rows),
        "Exact duplicate geolocation rows beyond their first occurrence.",
    )

    add_metric(
        "geolocation",
        "zip_prefixes_with_multiple_rows",
        int(zip_prefixes_with_multiple_rows),
        (
            "ZIP-code prefixes represented by multiple source rows, "
            "confirming that ZIP prefix is not a unique source key."
        ),
    )

    add_metric(
        "geolocation",
        "max_rows_per_zip_prefix",
        int(max_rows_per_zip_prefix),
        "Maximum geolocation observations associated with one ZIP prefix.",
    )

    return (
        pd.DataFrame(dataset_metrics),
        order_status_distribution,
    )


def save_reports(
    table_profile: pd.DataFrame,
    column_profile: pd.DataFrame,
    key_profile: pd.DataFrame,
    relationship_profile: pd.DataFrame,
    dataset_specific_profile: pd.DataFrame,
    order_status_distribution: pd.DataFrame,
) -> None:
    """
    Save all profiling outputs as CSV files.
    """

    # Create the reports directory if necessary.
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_outputs = {
        "source_table_profile.csv":
            table_profile,
        "source_column_profile.csv":
            column_profile,
        "source_key_profile.csv":
            key_profile,
        "source_relationship_profile.csv":
            relationship_profile,
        "dataset_specific_profile.csv":
            dataset_specific_profile,
        "order_status_distribution.csv":
            order_status_distribution,
    }

    # Loop through the report mapping so adding future reports requires
    # less repetitive export code.
    for file_name, report_df in report_outputs.items():

        output_path = REPORT_DIR / file_name

        report_df.to_csv(
            output_path,
            index=False,
        )

    print("\nProfiling reports saved:")

    for file_name in report_outputs:
        print(f"- {REPORT_DIR / file_name}")


def main() -> None:
    """
    Execute the complete source-data profiling workflow.
    """

    print("\nExecutive Commerce Intelligence Platform")
    print("Source Data Profiling")
    print("-" * 60)

    # ------------------------------------------------------------------
    # Structural and column profiling
    # ------------------------------------------------------------------

    table_profile, column_profile = run_profiling()

    print("\nSource Table Profile")
    print("-" * 60)

    print(
        table_profile.to_string(
            index=False
        )
    )

    print(
        f"\nColumns profiled: {len(column_profile)}"
    )

    # ------------------------------------------------------------------
    # Key validation
    # ------------------------------------------------------------------

    key_profile = validate_source_keys()

    print("\nSource Key Validation")
    print("-" * 60)

    print(
        key_profile.to_string(
            index=False
        )
    )

    # ------------------------------------------------------------------
    # Relationship validation
    # ------------------------------------------------------------------

    relationship_profile = validate_source_relationships()

    print("\nSource Relationship Validation")
    print("-" * 60)

    print(
        relationship_profile.to_string(
            index=False
        )
    )

    # ------------------------------------------------------------------
    # Dataset-specific profiling
    # ------------------------------------------------------------------

    (
        dataset_specific_profile,
        order_status_distribution,
    ) = run_dataset_specific_profiling()

    print("\nDataset-Specific Profile")
    print("-" * 60)

    print(
        dataset_specific_profile.to_string(
            index=False
        )
    )

    print("\nOrder Status Distribution")
    print("-" * 60)

    print(
        order_status_distribution.to_string(
            index=False
        )
    )

    # Save reports only after every profiling stage has succeeded.
    # This prevents a partially updated report set if execution fails.
    save_reports(
        table_profile=table_profile,
        column_profile=column_profile,
        key_profile=key_profile,
        relationship_profile=relationship_profile,
        dataset_specific_profile=dataset_specific_profile,
        order_status_distribution=order_status_distribution,
    )

    print("\nProfiling completed successfully.")


# Execute the workflow only when this file is run directly.
#
# If it is imported by another module in the future,
# main() will not execute automatically.
if __name__ == "__main__":
    main()
