# ============================================================
# STREAMLIT DASHBOARD
# Marketing Intelligence Platform
# ============================================================

"""
This dashboard is the frontend BI layer of the project.

Important:
----------
This file does not perform ETL.

Run the backend pipeline first:

    python main.py

That creates:

    marketing.db
    └── master_data

Then run:

    streamlit run dashboard/app.py
"""

# ============================================================
# IMPORTS
# ============================================================

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine


# ============================================================
# PROJECT PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import DATABASE_URL
from src.analytics.kpi import calculate_kpis


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Marketing Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PLOTLY CONFIG
# ============================================================

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True
}


# ============================================================
# PROFESSIONAL DASHBOARD CSS
# ============================================================

st.markdown(
    """
    <style>
        /* Main app container */
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }

        /* Header */
        .main-header {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5ff 100%);
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 1.4rem 1.7rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        .main-title {
            font-size: 2rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }

        .main-subtitle {
            font-size: 0.95rem;
            color: #64748b;
            margin-bottom: 0;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 750;
            color: #0f172a;
            margin-top: 0.4rem;
            margin-bottom: 0.9rem;
        }

        /* KPI cards */
        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b;
            font-weight: 650;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-size: 1.55rem;
            font-weight: 800;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }

        section[data-testid="stSidebar"] h1 {
            font-size: 1.5rem;
            color: #0f172a;
        }

        section[data-testid="stSidebar"] label {
            color: #0f172a;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] .stMetric {
            background: #ffffff;
        }

        /* Data grain explanation */
        .grain-card {
            background: #eef4ff;
            border-left: 5px solid #2563eb;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin: 1rem 0 1.2rem 0;
            color: #1e293b;
            font-size: 0.95rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        }

        /* Plotly chart cards */
        div[data-testid="stPlotlyChart"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            margin-bottom: 1.2rem;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-weight: 600;
            border-radius: 10px 10px 0 0;
        }

        /* Inputs */
        div[data-testid="stDateInput"] input {
            background-color: #f8fafc;
            border-radius: 12px;
        }

        div[data-testid="stSelectbox"] {
            margin-bottom: 0.8rem;
        }

        div[data-testid="stMultiSelect"] {
            margin-bottom: 0.8rem;
        }

        hr {
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FORMAT HELPERS
# ============================================================

def format_currency(value: float) -> str:
    """
    Formats revenue values for display.
    """

    if value is None or pd.isna(value):
        return "0"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{value:,.0f}"


def format_number(value: float) -> str:
    """
    Formats count values.
    """

    if value is None or pd.isna(value):
        return "0"

    return f"{value:,.0f}"


def format_percentage(value: float) -> str:
    """
    Formats percentage values.
    """

    if value is None or pd.isna(value):
        return "0.00%"

    return f"{value:.2f}%"


def apply_chart_layout(fig, height: int = 430):
    """
    Applies consistent BI-style layout to Plotly charts.
    """

    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=70, b=35),
        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#0f172a"
            )
        ),
        font=dict(
            family="Arial",
            size=13,
            color="#334155"
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_color="#0f172a"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        gridcolor="#e5e7eb",
        zeroline=False
    )

    return fig


def show_chart(fig):
    """
    Displays Plotly chart with consistent config.
    """

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(show_spinner="Loading curated master_data...")
def load_master_data() -> pd.DataFrame:
    """
    Loads the curated master_data table from SQLite.
    """

    engine = create_engine(DATABASE_URL)

    query = "SELECT * FROM master_data"

    df = pd.read_sql(query, engine)

    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts date fields into datetime.
    """

    df = df.copy()

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# SIDEBAR FILTERS
# ============================================================

def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies dashboard filters.

    Empty dropdown selections mean "include all values".
    This keeps the sidebar clean and avoids many selected chips.
    """

    st.sidebar.title("Filters")

    st.sidebar.caption(
        "Use filters to narrow the dashboard. Empty selections include all values."
    )

    filtered = df.copy()

    # Date filter
    if "order_purchase_timestamp" in filtered.columns:
        valid_dates = filtered["order_purchase_timestamp"].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            selected_dates = st.sidebar.date_input(
                "Order purchase date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                start_date, end_date = selected_dates

                filtered = filtered[
                    (filtered["order_purchase_timestamp"].dt.date >= start_date)
                    & (filtered["order_purchase_timestamp"].dt.date <= end_date)
                ]

    st.sidebar.divider()

    # Order status filter
    if "order_status" in filtered.columns:
        statuses = sorted(
            filtered["order_status"].dropna().unique()
        )

        selected_statuses = st.sidebar.multiselect(
            "Order status",
            options=statuses,
            default=[],
            placeholder="All statuses"
        )

        if selected_statuses:
            filtered = filtered[
                filtered["order_status"].isin(selected_statuses)
            ]

    # Customer state filter
    if "customer_state" in filtered.columns:
        states = sorted(
            filtered["customer_state"].dropna().unique()
        )

        selected_states = st.sidebar.multiselect(
            "Customer state",
            options=states,
            default=[],
            placeholder="All states"
        )

        if selected_states:
            filtered = filtered[
                filtered["customer_state"].isin(selected_states)
            ]

    # Product category filter
    category_column = None

    if "main_product_category_english" in filtered.columns:
        category_column = "main_product_category_english"
    elif "main_product_category" in filtered.columns:
        category_column = "main_product_category"

    if category_column:
        categories = sorted(
            filtered[category_column].dropna().unique()
        )

        selected_category = st.sidebar.selectbox(
            "Product category",
            options=["All categories"] + categories,
            index=0
        )

        if selected_category != "All categories":
            filtered = filtered[
                filtered[category_column] == selected_category
            ]

    st.sidebar.divider()

    st.sidebar.metric(
        "Filtered orders",
        f"{filtered['order_id'].nunique():,}"
        if "order_id" in filtered.columns
        else f"{len(filtered):,}"
    )

    st.sidebar.metric(
        "Filtered revenue",
        format_currency(filtered["payment_value"].sum())
        if "payment_value" in filtered.columns
        else "N/A"
    )

    return filtered


# ============================================================
# KPI SECTION
# ============================================================

def show_kpi_cards(df: pd.DataFrame):
    """
    Displays executive KPI cards.
    """

    kpis = calculate_kpis(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        format_currency(kpis.get("total_revenue", 0)),
        help="Sum of payment_value"
    )

    col2.metric(
        "Delivered Revenue",
        format_currency(kpis.get("delivered_revenue", 0)),
        help="Revenue from delivered orders only"
    )

    col3.metric(
        "Total Orders",
        format_number(kpis.get("total_orders", 0)),
        help="Unique order_id count"
    )

    col4.metric(
        "Average Order Value",
        format_currency(kpis.get("average_order_value", 0)),
        help="Total revenue divided by total orders"
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Unique Customers",
        format_number(kpis.get("unique_customers", 0)),
        help="Based on customer_unique_id"
    )

    col6.metric(
        "Orders per Customer",
        f"{kpis.get('orders_per_customer', 0):.2f}",
        help="Average number of orders per unique customer"
    )

    col7.metric(
        "Repeat Customer Rate",
        format_percentage(kpis.get("repeat_customer_rate", 0)),
        help="Customers with more than one order"
    )

    col8.metric(
        "Late Delivery Rate",
        format_percentage(kpis.get("late_delivery_rate", 0)),
        help="Orders delivered later than estimated date"
    )


# ============================================================
# CHARTS
# ============================================================

def chart_monthly_revenue(df: pd.DataFrame):
    """
    Monthly revenue trend.
    """

    required = {"order_purchase_timestamp", "payment_value"}

    if not required.issubset(df.columns):
        st.warning("Monthly revenue chart skipped.")
        return

    monthly = (
        df.dropna(subset=["order_purchase_timestamp"])
        .groupby(df["order_purchase_timestamp"].dt.to_period("M"))
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    monthly["month"] = monthly["order_purchase_timestamp"].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(
                width=3,
                color="#2563EB"
            ),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.12)",
            hovertemplate="Month: %{x}<br>Revenue: %{y:,.0f}<extra></extra>"
        )
    )

    fig.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue"
    )

    fig = apply_chart_layout(fig, height=460)

    show_chart(fig)


def chart_revenue_vs_orders(df: pd.DataFrame):
    """
    Monthly revenue and order volume.
    """

    required = {
        "order_purchase_timestamp",
        "payment_value",
        "order_id"
    }

    if not required.issubset(df.columns):
        st.warning("Revenue vs orders chart skipped.")
        return

    monthly = (
        df.dropna(subset=["order_purchase_timestamp"])
        .groupby(df["order_purchase_timestamp"].dt.to_period("M"))
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    monthly["month"] = monthly["order_purchase_timestamp"].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=monthly["month"],
            y=monthly["revenue"],
            name="Revenue",
            marker_color="#93C5FD",
            yaxis="y1",
            hovertemplate="Revenue: %{y:,.0f}<extra></extra>"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["orders"],
            name="Orders",
            mode="lines+markers",
            line=dict(
                width=3,
                color="#0F172A"
            ),
            yaxis="y2",
            hovertemplate="Orders: %{y:,.0f}<extra></extra>"
        )
    )

    fig.update_layout(
        title="Revenue and Order Volume",
        xaxis=dict(title="Month"),
        yaxis=dict(title="Revenue"),
        yaxis2=dict(
            title="Orders",
            overlaying="y",
            side="right"
        )
    )

    fig = apply_chart_layout(fig, height=460)

    show_chart(fig)


def chart_top_categories(df: pd.DataFrame):
    """
    Top categories by revenue.
    """

    category_column = None

    if "main_product_category_english" in df.columns:
        category_column = "main_product_category_english"
    elif "main_product_category" in df.columns:
        category_column = "main_product_category"

    if category_column is None or "payment_value" not in df.columns:
        st.warning("Category chart skipped.")
        return

    categories = (
        df.dropna(subset=[category_column])
        .groupby(category_column)
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .sort_values("revenue", ascending=False)
        .head(12)
        .reset_index()
    )

    fig = px.bar(
        categories.sort_values("revenue"),
        x="revenue",
        y=category_column,
        orientation="h",
        title="Top Product Categories by Revenue",
        text="revenue",
        hover_data=["orders"],
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Product Category"
    )

    fig = apply_chart_layout(fig, height=560)

    show_chart(fig)


def chart_order_status(df: pd.DataFrame):
    """
    Order status share.
    """

    if "order_status" not in df.columns:
        st.warning("Order status chart skipped.")
        return

    status = (
        df["order_status"]
        .value_counts(normalize=True)
        .mul(100)
        .reset_index()
    )

    status.columns = ["order_status", "share"]

    fig = px.bar(
        status,
        x="order_status",
        y="share",
        title="Order Status Share",
        text=status["share"].round(1),
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Order Status",
        yaxis_title="Share of Orders (%)"
    )

    fig = apply_chart_layout(fig, height=430)

    show_chart(fig)


def chart_payment_methods(df: pd.DataFrame):
    """
    Payment method share.
    """

    payment_column = None

    if "primary_payment_type" in df.columns:
        payment_column = "primary_payment_type"
    elif "payment_type" in df.columns:
        payment_column = "payment_type"

    if payment_column is None:
        st.warning("Payment method chart skipped.")
        return

    payment = (
        df[payment_column]
        .dropna()
        .value_counts(normalize=True)
        .mul(100)
        .reset_index()
    )

    payment.columns = ["payment_type", "share"]

    fig = px.bar(
        payment,
        x="payment_type",
        y="share",
        title="Payment Method Share",
        text=payment["share"].round(1),
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Payment Type",
        yaxis_title="Share of Orders (%)"
    )

    fig = apply_chart_layout(fig, height=430)

    show_chart(fig)


def chart_customer_frequency(df: pd.DataFrame):
    """
    Customer purchase frequency.
    """

    required = {"customer_unique_id", "order_id"}

    if not required.issubset(df.columns):
        st.warning("Customer frequency chart skipped.")
        return

    customer_orders = (
        df.groupby("customer_unique_id")["order_id"]
        .nunique()
        .reset_index()
    )

    customer_orders.columns = ["customer_unique_id", "orders"]

    fig = px.histogram(
        customer_orders,
        x="orders",
        nbins=30,
        title="Customer Purchase Frequency",
        labels={"orders": "Orders per Customer"},
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_layout(
        yaxis_title="Number of Customers"
    )

    fig = apply_chart_layout(fig, height=430)

    show_chart(fig)


def chart_customer_states(df: pd.DataFrame):
    """
    Revenue by customer state.
    """

    required = {"customer_state", "payment_value", "order_id"}

    if not required.issubset(df.columns):
        st.warning("Customer state chart skipped.")
        return

    states = (
        df.dropna(subset=["customer_state"])
        .groupby("customer_state")
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .sort_values("revenue", ascending=False)
        .reset_index()
    )

    fig = px.bar(
        states,
        x="customer_state",
        y="revenue",
        title="Revenue by Customer State",
        text="revenue",
        hover_data=["orders"],
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Customer State",
        yaxis_title="Revenue"
    )

    fig = apply_chart_layout(fig, height=470)

    show_chart(fig)


def chart_delivery_delay(df: pd.DataFrame):
    """
    Delivery delay distribution.
    """

    if "delivery_delay_days" not in df.columns:
        st.warning("Delivery chart skipped.")
        return

    delivery = df.dropna(subset=["delivery_delay_days"])

    if delivery.empty:
        st.warning("No delivery delay data available.")
        return

    fig = px.histogram(
        delivery,
        x="delivery_delay_days",
        nbins=70,
        title="Delivery Delay Distribution",
        labels={"delivery_delay_days": "Delivery Delay Days"},
        color_discrete_sequence=["#2563EB"]
    )

    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Estimated date",
        annotation_position="top"
    )

    fig.update_layout(
        yaxis_title="Number of Orders"
    )

    fig = apply_chart_layout(fig, height=430)

    show_chart(fig)


def chart_top_sellers(df: pd.DataFrame):
    """
    Top sellers by revenue.
    """

    seller_column = None

    if "main_seller_id" in df.columns:
        seller_column = "main_seller_id"
    elif "seller_id" in df.columns:
        seller_column = "seller_id"

    if seller_column is None or "payment_value" not in df.columns:
        st.warning("Seller chart skipped.")
        return

    sellers = (
        df.dropna(subset=[seller_column])
        .groupby(seller_column)
        .agg(
            revenue=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .sort_values("revenue", ascending=False)
        .head(12)
        .reset_index()
    )

    fig = px.bar(
        sellers.sort_values("revenue"),
        x="revenue",
        y=seller_column,
        orientation="h",
        title="Top Sellers by Revenue",
        text="revenue",
        hover_data=["orders"],
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Seller"
    )

    fig = apply_chart_layout(fig, height=560)

    show_chart(fig)


# ============================================================
# DATA QUALITY
# ============================================================

def show_data_quality(df: pd.DataFrame):
    """
    Shows simple data quality indicators.
    """

    duplicate_orders = (
        df["order_id"].duplicated().sum()
        if "order_id" in df.columns
        else None
    )

    missing_payments = (
        df["payment_value"].isna().sum()
        if "payment_value" in df.columns
        else None
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Rows",
        f"{len(df):,}"
    )

    col2.metric(
        "Duplicate order_id rows",
        f"{duplicate_orders:,}" if duplicate_orders is not None else "N/A"
    )

    col3.metric(
        "Missing payment values",
        f"{missing_payments:,}" if missing_payments is not None else "N/A"
    )


# ============================================================
# MAIN APP
# ============================================================

def main():
    """
    Runs the dashboard.
    """

    st.markdown(
        """
        <div class="main-header">
            <div class="main-title">📊 Marketing Intelligence Platform</div>
            <div class="main-subtitle">
                Executive analytics dashboard built on top of the Olist e-commerce ETL pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:
        df = load_master_data()
    except Exception as error:
        st.error("Could not load `master_data` from `marketing.db`.")
        st.info("Run `python main.py` first from the project root.")
        st.exception(error)
        return

    df = prepare_data(df)

    filtered_df = apply_sidebar_filters(df)

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    st.markdown(
        '<div class="section-title">Executive Overview</div>',
        unsafe_allow_html=True
    )

    show_kpi_cards(filtered_df)

    st.markdown(
        """
        <div class="grain-card">
            <b>Data model:</b> one row represents one order.
            Payments and items are aggregated before merging to prevent inflated revenue.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Revenue",
            "Customers",
            "Operations",
            "Products & Sellers",
            "Data Quality"
        ]
    )

    with tab1:
        chart_monthly_revenue(filtered_df)
        chart_revenue_vs_orders(filtered_df)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            chart_customer_frequency(filtered_df)

        with col2:
            chart_customer_states(filtered_df)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            chart_order_status(filtered_df)

        with col2:
            chart_payment_methods(filtered_df)

        chart_delivery_delay(filtered_df)

    with tab4:
        chart_top_categories(filtered_df)
        chart_top_sellers(filtered_df)

    with tab5:
        show_data_quality(filtered_df)

        with st.expander("Preview filtered dataset"):
            st.dataframe(
                filtered_df.head(200),
                use_container_width=True
            )

        with st.expander("Available columns"):
            st.write(list(filtered_df.columns))


if __name__ == "__main__":
    main()