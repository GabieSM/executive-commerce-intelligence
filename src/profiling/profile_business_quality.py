from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

# Resolve the absolute location of this script.
CURRENT_FILE = Path(__file__).resolve()

# Move from:
# src/profiling/profile_business_quality.py
# to the project root.
PROJECT_ROOT = CURRENT_FILE.parents[2]

# Define the raw-data location.
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Define where generated profiling reports will be stored.
REPORT_DIR = PROJECT_ROOT / "reports" / "profiling"


# ---------------------------------------------------------------------------
# Source files required for business-quality profiling
# ---------------------------------------------------------------------------

# This profiling module does not need every Olist source.
# Only datasets relevant to timestamps, monetary values, payments,
# deliveries, and customer reviews are loaded.
SOURCE_FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
}


# ---------------------------------------------------------------------------
# Timestamp configuration
# ---------------------------------------------------------------------------

# Define datetime fields that should be validated.
#
# CSV files do not contain native datetime data types, so pandas initially
# reads these values as strings/objects. This profiling step verifies
# whether those values can be safely converted to timestamps.
TIMESTAMP_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "shipping_limit_date",
    ],
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


def load_sources() -> dict[str, pd.DataFrame]:
    """
    Load the raw datasets required for business-quality profiling.

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping between source names and their pandas DataFrames.
    """

    sources = {}

    for source_name, file_name in SOURCE_FILES.items():

        file_path = RAW_DATA_DIR / file_name

        # Stop execution if an expected source is missing.
        # Profiling incomplete source data could produce misleading results.
        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        print(f"Loading {source_name}: {file_name}")

        sources[source_name] = pd.read_csv(
            file_path,
            low_memory=False,
        )

    return sources


def build_timestamp_quality_profile(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Validate timestamp completeness, parsing, and observed date ranges.

    The source CSVs contain timestamps as text. This function determines:
    - how many values are missing;
    - whether non-null values can be converted to datetime;
    - the minimum observed timestamp;
    - the maximum observed timestamp.
    """

    profiles = []

    for source_name, columns in TIMESTAMP_COLUMNS.items():

        df = sources[source_name]

        for column_name in columns:

            raw_series = df[column_name]

            # Convert source values into pandas datetime values.
            #
            # errors="coerce" converts invalid timestamp strings to NaT
            # rather than stopping the pipeline.
            parsed_series = pd.to_datetime(
                raw_series,
                errors="coerce",
            )

            # Count original non-null values.
            non_null_raw_count = raw_series.notna().sum()

            # A parse failure occurs when the original value exists
            # but pandas cannot interpret it as a datetime.
            parse_failure_count = (
                raw_series.notna()
                & parsed_series.isna()
            ).sum()

            profiles.append(
                {
                    "source_name": source_name,
                    "column_name": column_name,
                    "row_count": len(df),
                    "null_count": int(
                        raw_series.isna().sum()
                    ),
                    "non_null_count": int(
                        non_null_raw_count
                    ),
                    "parse_failure_count": int(
                        parse_failure_count
                    ),
                    "min_timestamp": (
                        parsed_series.min()
                        if parsed_series.notna().any()
                        else None
                    ),
                    "max_timestamp": (
                        parsed_series.max()
                        if parsed_series.notna().any()
                        else None
                    ),
                }
            )

    return pd.DataFrame(profiles)


def build_temporal_consistency_profile(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """
    Test whether important order timestamps occur in a logical sequence.

    These checks identify data-quality exceptions without automatically
    removing or correcting records.
    """

    df = orders.copy()

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    # Convert the relevant order fields to real datetime values
    # before comparing timestamps.
    for column_name in timestamp_columns:
        df[column_name] = pd.to_datetime(
            df[column_name],
            errors="coerce",
        )

    profiles = []

    def add_temporal_check(
        check_name: str,
        comparable_mask: pd.Series,
        violation_mask: pd.Series,
        interpretation: str,
    ) -> None:
        """
        Add one standardized temporal-consistency validation result.
        """

        comparable_count = comparable_mask.sum()

        violation_count = (
            comparable_mask
            & violation_mask
        ).sum()

        violation_percentage = (
            (violation_count / comparable_count) * 100
            if comparable_count > 0
            else 0.0
        )

        profiles.append(
            {
                "check_name": check_name,
                "comparable_row_count": int(
                    comparable_count
                ),
                "violation_count": int(
                    violation_count
                ),
                "violation_percentage": round(
                    violation_percentage,
                    4,
                ),
                "interpretation": interpretation,
            }
        )

    # Approval should normally not occur before the purchase itself.
    comparable = (
        df["order_purchase_timestamp"].notna()
        & df["order_approved_at"].notna()
    )

    add_temporal_check(
        "approval_before_purchase",
        comparable,
        (
            df["order_approved_at"]
            < df["order_purchase_timestamp"]
        ),
        "Order approval occurs before the recorded purchase timestamp.",
    )

    # Carrier handoff is expected to occur after order approval.
    comparable = (
        df["order_approved_at"].notna()
        & df["order_delivered_carrier_date"].notna()
    )

    add_temporal_check(
        "carrier_handoff_before_approval",
        comparable,
        (
            df["order_delivered_carrier_date"]
            < df["order_approved_at"]
        ),
        "Carrier handoff occurs before the recorded order approval.",
    )

    # Customer delivery should normally occur after carrier handoff.
    comparable = (
        df["order_delivered_carrier_date"].notna()
        & df["order_delivered_customer_date"].notna()
    )

    add_temporal_check(
        "customer_delivery_before_carrier_handoff",
        comparable,
        (
            df["order_delivered_customer_date"]
            < df["order_delivered_carrier_date"]
        ),
        "Customer delivery occurs before the recorded carrier handoff.",
    )

    # Customer delivery should never logically precede the purchase.
    comparable = (
        df["order_purchase_timestamp"].notna()
        & df["order_delivered_customer_date"].notna()
    )

    add_temporal_check(
        "customer_delivery_before_purchase",
        comparable,
        (
            df["order_delivered_customer_date"]
            < df["order_purchase_timestamp"]
        ),
        "Customer delivery occurs before the recorded purchase.",
    )

    # Estimated delivery should not normally precede the purchase date.
    comparable = (
        df["order_purchase_timestamp"].notna()
        & df["order_estimated_delivery_date"].notna()
    )

    add_temporal_check(
        "estimated_delivery_before_purchase",
        comparable,
        (
            df["order_estimated_delivery_date"]
            < df["order_purchase_timestamp"]
        ),
        "Estimated delivery occurs before the recorded purchase.",
    )

    return pd.DataFrame(profiles)


def build_monetary_profile(
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
) -> pd.DataFrame:
    """
    Profile the principal monetary measures in the source data.

    Distribution statistics help identify:
    - negative values;
    - zero values;
    - extreme values;
    - potentially unusual observations.
    """

    measures = [
        (
            "order_items",
            "price",
            order_items["price"],
        ),
        (
            "order_items",
            "freight_value",
            order_items["freight_value"],
        ),
        (
            "payments",
            "payment_value",
            payments["payment_value"],
        ),
    ]

    profiles = []

    for source_name, column_name, series in measures:

        profiles.append(
            {
                "source_name": source_name,
                "column_name": column_name,
                "row_count": len(series),
                "null_count": int(
                    series.isna().sum()
                ),
                "negative_count": int(
                    (series < 0).sum()
                ),
                "zero_count": int(
                    (series == 0).sum()
                ),
                "minimum": round(
                    float(series.min()),
                    4,
                ),
                "p01": round(
                    float(series.quantile(0.01)),
                    4,
                ),
                "median": round(
                    float(series.median()),
                    4,
                ),
                "mean": round(
                    float(series.mean()),
                    4,
                ),
                "p95": round(
                    float(series.quantile(0.95)),
                    4,
                ),
                "p99": round(
                    float(series.quantile(0.99)),
                    4,
                ),
                "maximum": round(
                    float(series.max()),
                    4,
                ),
            }
        )

    return pd.DataFrame(profiles)


def build_payment_reconciliation_profile(
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare order merchandise + freight totals against payment totals.

    Monetary values are converted to integer cents before reconciliation.
    This avoids floating-point precision problems when comparing currency.

    Order Items and Payments have different grains, so both datasets
    must first be aggregated to one row per order.
    """

    # Create a working copy so the original source DataFrame remains unchanged.
    items = order_items.copy()
    payment_data = payments.copy()

    # Convert monetary values from decimal currency units into integer cents.
    #
    # Example:
    # 10.99 -> 1099 cents
    #
    # Integer arithmetic is safer for currency reconciliation because
    # binary floating-point numbers cannot represent every decimal value
    # exactly.
    items["price_cents"] = (
        items["price"] * 100
    ).round().astype("int64")

    items["freight_cents"] = (
        items["freight_value"] * 100
    ).round().astype("int64")

    payment_data["payment_cents"] = (
        payment_data["payment_value"] * 100
    ).round().astype("int64")

    # Aggregate item-level monetary values to one row per order.
    order_item_totals = (
        items
        .groupby(
            "order_id",
            as_index=False,
        )
        .agg(
            item_value_cents=("price_cents", "sum"),
            freight_value_cents=("freight_cents", "sum"),
        )
    )

    # Calculate the total source amount represented by merchandise
    # plus freight at order grain.
    order_item_totals["item_plus_freight_cents"] = (
        order_item_totals["item_value_cents"]
        + order_item_totals["freight_value_cents"]
    )

    # Aggregate potentially multiple payment rows to one row per order.
    payment_totals = (
        payment_data
        .groupby(
            "order_id",
            as_index=False,
        )
        .agg(
            payment_value_cents=("payment_cents", "sum")
        )
    )

    # Outer join preserves orders that appear on only one side.
    reconciliation = order_item_totals.merge(
        payment_totals,
        on="order_id",
        how="outer",
        indicator=True,
    )

    # Comparable orders are present in both Order Items and Payments.
    comparable_mask = (
        reconciliation["_merge"] == "both"
    )

    # Calculate the exact difference in integer cents.
    reconciliation["difference_cents"] = (
        reconciliation["payment_value_cents"]
        - reconciliation["item_plus_freight_cents"]
    )

    # Exact reconciliation means both totals are identical to the cent.
    exact_match_mask = (
        comparable_mask
        & (reconciliation["difference_cents"] == 0)
    )

    # Allow a one-cent tolerance as a separate quality measure.
    #
    # This does not modify the underlying data. It simply recognizes
    # that a one-cent difference is immaterial for this validation.
    within_one_cent_mask = (
        comparable_mask
        & (
            reconciliation["difference_cents"]
            .abs()
            <= 1
        )
    )

    # Material exceptions are comparable orders whose absolute
    # difference exceeds one cent.
    exception_mask = (
        comparable_mask
        & (
            reconciliation["difference_cents"]
            .abs()
            > 1
        )
    )

    comparable_count = int(
        comparable_mask.sum()
    )

    exact_reconciliation_rate = (
        exact_match_mask.sum()
        / comparable_count
        * 100
        if comparable_count > 0
        else 0.0
    )

    one_cent_reconciliation_rate = (
        within_one_cent_mask.sum()
        / comparable_count
        * 100
        if comparable_count > 0
        else 0.0
    )

    # Convert the largest observed difference back into normal
    # currency units for easier interpretation.
    maximum_absolute_difference = (
        reconciliation.loc[
            comparable_mask,
            "difference_cents",
        ]
        .abs()
        .max()
        / 100
    )

    metrics = [
        {
            "metric_name": "orders_with_item_values",
            "metric_value": len(order_item_totals),
        },
        {
            "metric_name": "orders_with_payment_values",
            "metric_value": len(payment_totals),
        },
        {
            "metric_name": "orders_present_in_both",
            "metric_value": comparable_count,
        },
        {
            "metric_name": "orders_with_items_but_no_payment",
            "metric_value": int(
                (
                    reconciliation["_merge"]
                    == "left_only"
                ).sum()
            ),
        },
        {
            "metric_name": "orders_with_payment_but_no_items",
            "metric_value": int(
                (
                    reconciliation["_merge"]
                    == "right_only"
                ).sum()
            ),
        },
        {
            "metric_name": "orders_reconciled_exactly",
            "metric_value": int(
                exact_match_mask.sum()
            ),
        },
        {
            "metric_name": "exact_reconciliation_rate_percentage",
            "metric_value": round(
                exact_reconciliation_rate,
                4,
            ),
        },
        {
            "metric_name": "orders_reconciled_within_one_cent",
            "metric_value": int(
                within_one_cent_mask.sum()
            ),
        },
        {
            "metric_name": "one_cent_reconciliation_rate_percentage",
            "metric_value": round(
                one_cent_reconciliation_rate,
                4,
            ),
        },
        {
            "metric_name": "orders_difference_above_one_cent",
            "metric_value": int(
                exception_mask.sum()
            ),
        },
        {
            "metric_name": "maximum_absolute_difference",
            "metric_value": round(
                float(maximum_absolute_difference),
                2,
            ),
        },
    ]

    return pd.DataFrame(metrics)


def build_delivery_quality_profile(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """
    Profile delivery completeness, lead time, and late-delivery behavior.

    Delivery KPIs are calculated using delivered orders because
    canceled or unfinished orders do not represent completed deliveries.
    """

    df = orders.copy()

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column_name in date_columns:
        df[column_name] = pd.to_datetime(
            df[column_name],
            errors="coerce",
        )

    # Restrict the primary delivery population to orders whose
    # source status is explicitly "delivered".
    delivered = df.loc[
        df["order_status"] == "delivered"
    ].copy()

    # Calculate customer delivery lead time in days.
    lead_time_mask = (
        delivered["order_purchase_timestamp"].notna()
        & delivered[
            "order_delivered_customer_date"
        ].notna()
    )

    lead_time_days = (
        delivered.loc[
            lead_time_mask,
            "order_delivered_customer_date",
        ]
        - delivered.loc[
            lead_time_mask,
            "order_purchase_timestamp",
        ]
    ).dt.total_seconds() / 86400

    # Compare actual delivery against the estimated delivery date.
    delivery_comparison_mask = (
        delivered[
            "order_delivered_customer_date"
        ].notna()
        & delivered[
            "order_estimated_delivery_date"
        ].notna()
    )

    days_early_late = (
        delivered.loc[
            delivery_comparison_mask,
            "order_delivered_customer_date",
        ]
        - delivered.loc[
            delivery_comparison_mask,
            "order_estimated_delivery_date",
        ]
    ).dt.total_seconds() / 86400

    # Positive values represent late deliveries.
    late_orders = (
        days_early_late > 0
    ).sum()

    late_delivery_rate = (
        (late_orders / len(days_early_late)) * 100
        if len(days_early_late) > 0
        else 0.0
    )

    metrics = [
        {
            "metric_name": "delivered_orders",
            "metric_value": len(delivered),
        },
        {
            "metric_name": "delivered_missing_approval_timestamp",
            "metric_value": int(
                delivered[
                    "order_approved_at"
                ].isna().sum()
            ),
        },
        {
            "metric_name": "delivered_missing_carrier_timestamp",
            "metric_value": int(
                delivered[
                    "order_delivered_carrier_date"
                ].isna().sum()
            ),
        },
        {
            "metric_name": "delivered_missing_customer_delivery_timestamp",
            "metric_value": int(
                delivered[
                    "order_delivered_customer_date"
                ].isna().sum()
            ),
        },
        {
            "metric_name": "delivery_lead_time_observations",
            "metric_value": len(
                lead_time_days
            ),
        },
        {
            "metric_name": "median_delivery_lead_time_days",
            "metric_value": round(
                float(lead_time_days.median()),
                4,
            ),
        },
        {
            "metric_name": "p95_delivery_lead_time_days",
            "metric_value": round(
                float(
                    lead_time_days.quantile(0.95)
                ),
                4,
            ),
        },
        {
            "metric_name": "maximum_delivery_lead_time_days",
            "metric_value": round(
                float(lead_time_days.max()),
                4,
            ),
        },
        {
            "metric_name": "delivery_estimate_comparisons",
            "metric_value": len(
                days_early_late
            ),
        },
        {
            "metric_name": "late_delivered_orders",
            "metric_value": int(
                late_orders
            ),
        },
        {
            "metric_name": "late_delivery_rate_percentage",
            "metric_value": round(
                late_delivery_rate,
                4,
            ),
        },
        {
            "metric_name": "median_days_early_late",
            "metric_value": round(
                float(days_early_late.median()),
                4,
            ),
        },
        {
            "metric_name": "maximum_days_late",
            "metric_value": round(
                float(days_early_late.max()),
                4,
            ),
        },
    ]

    return pd.DataFrame(metrics)


def build_review_profiles(
    reviews: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Profile review-score validity, distribution, and satisfaction groups.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Review summary metrics and score distribution.
    """

    score = reviews["review_score"]

    # Olist review scores are expected to fall between 1 and 5.
    valid_score_mask = score.between(
        1,
        5,
        inclusive="both",
    )

    valid_scores = score.loc[
        valid_score_mask
    ]

    low_review_mask = (
        valid_scores <= 2
    )

    high_review_mask = (
        valid_scores >= 4
    )

    summary = pd.DataFrame(
        [
            {
                "metric_name": "review_rows",
                "metric_value": len(reviews),
            },
            {
                "metric_name": "valid_review_scores",
                "metric_value": len(valid_scores),
            },
            {
                "metric_name": "invalid_review_scores",
                "metric_value": int(
                    (~valid_score_mask).sum()
                ),
            },
            {
                "metric_name": "average_review_score",
                "metric_value": round(
                    float(valid_scores.mean()),
                    4,
                ),
            },
            {
                "metric_name": "median_review_score",
                "metric_value": round(
                    float(valid_scores.median()),
                    4,
                ),
            },
            {
                "metric_name": "low_review_rate_percentage",
                "metric_value": round(
                    low_review_mask.mean() * 100,
                    4,
                ),
            },
            {
                "metric_name": "high_review_rate_percentage",
                "metric_value": round(
                    high_review_mask.mean() * 100,
                    4,
                ),
            },
        ]
    )

    # Build the full score distribution for scores 1 through 5.
    distribution = (
        valid_scores
        .value_counts()
        .sort_index()
        .rename_axis("review_score")
        .reset_index(name="review_count")
    )

    distribution[
        "percentage"
    ] = (
        distribution["review_count"]
        / len(valid_scores)
        * 100
    ).round(4)

    return summary, distribution


def save_reports(
    reports: dict[str, pd.DataFrame],
) -> None:
    """
    Save all business-quality profiling reports to CSV files.
    """

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nBusiness-quality reports saved:")

    for file_name, report_df in reports.items():

        output_path = REPORT_DIR / file_name

        report_df.to_csv(
            output_path,
            index=False,
        )

        print(f"- {output_path}")


def main() -> None:
    """
    Execute business and data-quality profiling.
    """

    print("\nExecutive Commerce Intelligence Platform")
    print("Business & Data Quality Profiling")
    print("-" * 60)

    sources = load_sources()

    timestamp_profile = (
        build_timestamp_quality_profile(
            sources
        )
    )

    temporal_consistency_profile = (
        build_temporal_consistency_profile(
            sources["orders"]
        )
    )

    monetary_profile = (
        build_monetary_profile(
            order_items=sources["order_items"],
            payments=sources["payments"],
        )
    )

    payment_reconciliation_profile = (
        build_payment_reconciliation_profile(
            order_items=sources["order_items"],
            payments=sources["payments"],
        )
    )

    delivery_quality_profile = (
        build_delivery_quality_profile(
            sources["orders"]
        )
    )

    (
        review_quality_profile,
        review_score_distribution,
    ) = build_review_profiles(
        sources["reviews"]
    )

    reports = {
        "timestamp_quality_profile.csv":
            timestamp_profile,
        "temporal_consistency_profile.csv":
            temporal_consistency_profile,
        "monetary_profile.csv":
            monetary_profile,
        "payment_reconciliation_profile.csv":
            payment_reconciliation_profile,
        "delivery_quality_profile.csv":
            delivery_quality_profile,
        "review_quality_profile.csv":
            review_quality_profile,
        "review_score_distribution.csv":
            review_score_distribution,
    }

    # Print the most decision-relevant quality outputs.
    print("\nTemporal Consistency")
    print("-" * 60)
    print(
        temporal_consistency_profile.to_string(
            index=False
        )
    )

    print("\nMonetary Profile")
    print("-" * 60)
    print(
        monetary_profile.to_string(
            index=False
        )
    )

    print("\nPayment Reconciliation")
    print("-" * 60)
    print(
        payment_reconciliation_profile.to_string(
            index=False
        )
    )

    print("\nDelivery Quality")
    print("-" * 60)
    print(
        delivery_quality_profile.to_string(
            index=False
        )
    )

    print("\nReview Quality")
    print("-" * 60)
    print(
        review_quality_profile.to_string(
            index=False
        )
    )

    save_reports(reports)

    print(
        "\nBusiness & data-quality profiling "
        "completed successfully."
    )


# Execute the workflow only when this script is run directly.
if __name__ == "__main__":
    main()