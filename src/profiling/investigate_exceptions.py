from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

# Resolve the location of this script and derive the project root.
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

# Define source-data and exception-report locations.
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
EXCEPTION_REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "profiling"
    / "exceptions"
)


# ---------------------------------------------------------------------------
# Source files
# ---------------------------------------------------------------------------

SOURCE_FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
}


def load_sources() -> dict[str, pd.DataFrame]:
    """
    Load the raw sources required for exception investigation.

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping between logical source names and DataFrames.
    """

    sources = {}

    for source_name, file_name in SOURCE_FILES.items():

        file_path = RAW_DATA_DIR / file_name

        # Stop execution when a required raw source is unavailable.
        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        print(
            f"Loading {source_name}: {file_name}"
        )

        sources[source_name] = pd.read_csv(
            file_path,
            low_memory=False,
        )

    return sources


def investigate_temporal_exceptions(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return order-level records that violate expected timestamp sequences.

    Each exception is stored as a separate row so that the underlying
    orders can be reviewed instead of being represented only by counts.
    """

    df = orders.copy()

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    # Convert source strings into datetime values before comparison.
    for column_name in timestamp_columns:
        df[column_name] = pd.to_datetime(
            df[column_name],
            errors="coerce",
        )

    exception_frames = []

    def add_exception(
        exception_type: str,
        mask: pd.Series,
        difference_hours: pd.Series,
    ) -> None:
        """
        Add detailed rows for one temporal exception type.
        """

        exception_df = df.loc[
            mask,
            [
                "order_id",
                "order_status",
                *timestamp_columns,
            ],
        ].copy()

        exception_df.insert(
            0,
            "exception_type",
            exception_type,
        )

        # Store the magnitude of the temporal inconsistency.
        # Positive values represent how many hours the sequence is reversed.
        exception_df[
            "exception_difference_hours"
        ] = difference_hours.loc[
            mask
        ].round(4)

        exception_frames.append(
            exception_df
        )

    # Approval occurring before purchase.
    mask = (
        df["order_purchase_timestamp"].notna()
        & df["order_approved_at"].notna()
        & (
            df["order_approved_at"]
            < df["order_purchase_timestamp"]
        )
    )

    add_exception(
        "approval_before_purchase",
        mask,
        (
            df["order_purchase_timestamp"]
            - df["order_approved_at"]
        ).dt.total_seconds() / 3600,
    )

    # Carrier handoff occurring before approval.
    mask = (
        df["order_approved_at"].notna()
        & df[
            "order_delivered_carrier_date"
        ].notna()
        & (
            df["order_delivered_carrier_date"]
            < df["order_approved_at"]
        )
    )

    add_exception(
        "carrier_handoff_before_approval",
        mask,
        (
            df["order_approved_at"]
            - df["order_delivered_carrier_date"]
        ).dt.total_seconds() / 3600,
    )

    # Customer delivery occurring before carrier handoff.
    mask = (
        df[
            "order_delivered_carrier_date"
        ].notna()
        & df[
            "order_delivered_customer_date"
        ].notna()
        & (
            df["order_delivered_customer_date"]
            < df["order_delivered_carrier_date"]
        )
    )

    add_exception(
        "customer_delivery_before_carrier_handoff",
        mask,
        (
            df["order_delivered_carrier_date"]
            - df["order_delivered_customer_date"]
        ).dt.total_seconds() / 3600,
    )

    # Return an empty DataFrame safely if no exceptions are found.
    if not exception_frames:
        return pd.DataFrame()

    return pd.concat(
        exception_frames,
        ignore_index=True,
    )


def investigate_payment_reconciliation(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return orders whose payment total differs from item + freight total
    by more than one cent.

    Currency is represented as integer cents to avoid floating-point
    precision problems.
    """

    items = order_items.copy()
    payment_data = payments.copy()

    # Convert currency values to integer cents before aggregation.
    items["price_cents"] = (
        items["price"] * 100
    ).round().astype("int64")

    items["freight_cents"] = (
        items["freight_value"] * 100
    ).round().astype("int64")

    payment_data["payment_cents"] = (
        payment_data["payment_value"] * 100
    ).round().astype("int64")

    # Aggregate commercial values to order grain.
    item_totals = (
        items
        .groupby(
            "order_id",
            as_index=False,
        )
        .agg(
            item_value_cents=("price_cents", "sum"),
            freight_value_cents=("freight_cents", "sum"),
            order_item_count=("order_item_id", "count"),
        )
    )

    item_totals["item_plus_freight_cents"] = (
        item_totals["item_value_cents"]
        + item_totals["freight_value_cents"]
    )

    # Aggregate all payment records to order grain.
    payment_totals = (
        payment_data
        .groupby(
            "order_id",
            as_index=False,
        )
        .agg(
            payment_value_cents=("payment_cents", "sum"),
            payment_record_count=(
                "payment_sequential",
                "count",
            ),
        )
    )

    reconciliation = item_totals.merge(
        payment_totals,
        on="order_id",
        how="inner",
    )

    # Calculate the exact difference at order grain.
    reconciliation["difference_cents"] = (
        reconciliation["payment_value_cents"]
        - reconciliation["item_plus_freight_cents"]
    )

    # Keep only material exceptions exceeding one cent.
    exceptions = reconciliation.loc[
        reconciliation[
            "difference_cents"
        ].abs() > 1
    ].copy()

    # Add order status to support business interpretation.
    exceptions = exceptions.merge(
        orders[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
            ]
        ],
        on="order_id",
        how="left",
    )

    # Convert integer cents back to decimal currency values
    # for easier review in the exported report.
    exceptions["item_value"] = (
        exceptions["item_value_cents"] / 100
    )

    exceptions["freight_value"] = (
        exceptions["freight_value_cents"] / 100
    )

    exceptions["item_plus_freight"] = (
        exceptions["item_plus_freight_cents"]
        / 100
    )

    exceptions["payment_value"] = (
        exceptions["payment_value_cents"]
        / 100
    )

    exceptions["difference_value"] = (
        exceptions["difference_cents"] / 100
    )

    # Present the most useful columns first.
    return exceptions[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_item_count",
            "payment_record_count",
            "item_value",
            "freight_value",
            "item_plus_freight",
            "payment_value",
            "difference_value",
            "difference_cents",
        ]
    ].sort_values(
        by="difference_cents",
        key=lambda series: series.abs(),
        ascending=False,
    )


def investigate_relationship_exceptions(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
    reviews: pd.DataFrame,
) -> pd.DataFrame:
    """
    Identify orders missing expected child records.

    This report does not automatically label the records as errors.
    Some missing relationships may be structurally expected for
    canceled, unavailable, or unfinished orders.
    """

    df = orders[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
        ]
    ].copy()

    # Create sets of order identifiers represented in each child table.
    item_order_ids = set(
        order_items["order_id"].unique()
    )

    payment_order_ids = set(
        payments["order_id"].unique()
    )

    review_order_ids = set(
        reviews["order_id"].unique()
    )

    # Indicate whether each order is represented in the child sources.
    df["has_order_items"] = (
        df["order_id"].isin(item_order_ids)
    )

    df["has_payments"] = (
        df["order_id"].isin(payment_order_ids)
    )

    df["has_reviews"] = (
        df["order_id"].isin(review_order_ids)
    )

    # Keep only orders missing at least one child relationship.
    exception_mask = (
        ~df["has_order_items"]
        | ~df["has_payments"]
        | ~df["has_reviews"]
    )

    exceptions = df.loc[
        exception_mask
    ].copy()

    # Create explicit flags that are easier to aggregate later.
    exceptions["missing_order_items"] = (
        ~exceptions["has_order_items"]
    )

    exceptions["missing_payments"] = (
        ~exceptions["has_payments"]
    )

    exceptions["missing_reviews"] = (
        ~exceptions["has_reviews"]
    )

    return exceptions


def build_exception_summary(
    temporal_exceptions: pd.DataFrame,
    payment_exceptions: pd.DataFrame,
    relationship_exceptions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a compact summary of exception counts.

    The summary provides quick visibility while detailed reports retain
    the underlying order-level evidence.
    """

    summary_records = []

    # Summarize temporal exceptions by exception type.
    if not temporal_exceptions.empty:

        temporal_counts = (
            temporal_exceptions[
                "exception_type"
            ]
            .value_counts()
        )

        for exception_type, count in temporal_counts.items():

            summary_records.append(
                {
                    "exception_domain": "temporal",
                    "exception_type": exception_type,
                    "exception_count": int(count),
                }
            )

    # Add the number of material payment reconciliation exceptions.
    summary_records.append(
        {
            "exception_domain": "payments",
            "exception_type":
                "difference_above_one_cent",
            "exception_count": len(
                payment_exceptions
            ),
        }
    )

    # Summarize missing child relationships independently.
    relationship_columns = {
        "missing_order_items":
            "orders_without_items",
        "missing_payments":
            "orders_without_payments",
        "missing_reviews":
            "orders_without_reviews",
    }

    for column_name, exception_type in (
        relationship_columns.items()
    ):

        summary_records.append(
            {
                "exception_domain": "relationships",
                "exception_type": exception_type,
                "exception_count": int(
                    relationship_exceptions[
                        column_name
                    ].sum()
                ),
            }
        )

    return pd.DataFrame(
        summary_records
    )


def save_reports(
    reports: dict[str, pd.DataFrame],
) -> None:
    """
    Save detailed exception reports to CSV.
    """

    # Create reports/profiling/exceptions if it does not already exist.
    EXCEPTION_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nException reports saved:")

    for file_name, report_df in reports.items():

        output_path = (
            EXCEPTION_REPORT_DIR / file_name
        )

        report_df.to_csv(
            output_path,
            index=False,
        )

        print(f"- {output_path}")


def main() -> None:
    """
    Execute detailed exception investigation.
    """

    print(
        "\nExecutive Commerce Intelligence Platform"
    )
    print("Source Exception Investigation")
    print("-" * 60)

    sources = load_sources()

    temporal_exceptions = (
        investigate_temporal_exceptions(
            sources["orders"]
        )
    )

    payment_exceptions = (
        investigate_payment_reconciliation(
            orders=sources["orders"],
            order_items=sources["order_items"],
            payments=sources["payments"],
        )
    )

    relationship_exceptions = (
        investigate_relationship_exceptions(
            orders=sources["orders"],
            order_items=sources["order_items"],
            payments=sources["payments"],
            reviews=sources["reviews"],
        )
    )

    exception_summary = (
        build_exception_summary(
            temporal_exceptions=
                temporal_exceptions,
            payment_exceptions=
                payment_exceptions,
            relationship_exceptions=
                relationship_exceptions,
        )
    )

    print("\nException Summary")
    print("-" * 60)

    print(
        exception_summary.to_string(
            index=False
        )
    )

    # Show how payment exceptions are distributed by order status.
    if not payment_exceptions.empty:

        print(
            "\nPayment Exceptions by Order Status"
        )
        print("-" * 60)

        print(
            payment_exceptions[
                "order_status"
            ]
            .value_counts()
            .to_string()
        )

    # Show order-status behavior for missing source relationships.
    print(
        "\nOrders Missing Items by Status"
    )
    print("-" * 60)

    print(
        relationship_exceptions.loc[
            relationship_exceptions[
                "missing_order_items"
            ],
            "order_status",
        ]
        .value_counts()
        .to_string()
    )

    reports = {
        "temporal_exceptions.csv":
            temporal_exceptions,
        "payment_reconciliation_exceptions.csv":
            payment_exceptions,
        "relationship_exceptions.csv":
            relationship_exceptions,
        "exception_summary.csv":
            exception_summary,
    }

    save_reports(
        reports
    )

    print(
        "\nException investigation "
        "completed successfully."
    )


# Execute the workflow only when this file is run directly.
if __name__ == "__main__":
    main()