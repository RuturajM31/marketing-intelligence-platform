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


Important business wording:
---------------------------
The column payment_value represents recorded payment value.

In the Olist dataset, canceled orders can still have payment_value.

Therefore:

    Gross Payment Value
        = sum of payment_value for selected orders, regardless of status

    Delivered Revenue
        = sum of payment_value only for delivered orders

This avoids showing misleading "revenue" for canceled orders.
"""

# ============================================================
# IMPORTS
# ============================================================

# sys allows us to add the project root to the Python path.
import sys

# Path helps us work with file paths safely.
from pathlib import Path

# pandas is used for dataframe operations.
import pandas as pd

# plotly.express creates charts with less code.
import plotly.express as px

# plotly.graph_objects is used for more customized charts.
import plotly.graph_objects as go

# streamlit is used to build the dashboard frontend.
import streamlit as st

# create_engine creates a connection to the SQLite database.
from sqlalchemy import create_engine


# ============================================================
# PROJECT PATH SETUP
# ============================================================

# __file__ points to dashboard/app.py.
# parents[1] moves one level up to the project root:
# marketing-intelligence-platform/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Add project root to Python path.
# This allows imports like:
# from src.analytics.kpi import calculate_kpis
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import KPI calculation logic from your analytics layer.
from src.analytics.kpi import calculate_kpis


# ============================================================
# DATABASE PATH
# ============================================================

# main.py creates marketing.db in the project root.
DB_PATH = PROJECT_ROOT / "marketing.db"

# SQLAlchemy database URL for SQLite.
DATABASE_URL = f"sqlite:///{DB_PATH}"


# ============================================================
# PAGE CONFIG
# ============================================================

# This must be called before most Streamlit UI code.
st.set_page_config(
    page_title="Marketing Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PLOTLY CONFIG
# ============================================================

# Hide the Plotly toolbar for a cleaner dashboard.
PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True
}


# ============================================================
# CUSTOM CSS
# ============================================================

# This CSS makes the dashboard look more professional.
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }

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

        div[data-testid="stPlotlyChart"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            margin-bottom: 1.2rem;
        }

        button[data-baseweb="tab"] {
            font-weight: 600;
            border-radius: 10px 10px 0 0;
        }

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
    Formats money values for dashboard display.

    Examples:
        16010000 -> 16.01M
        143300   -> 143.3K
        229      -> 229
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

    Example:
        99441 -> 99,441
    """

    if value is None or pd.isna(value):
        return "0"

    return f"{value:,.0f}"


def format_percentage(value: float) -> str:
    """
    Formats percentage values.

    Example:
        3.124 -> 3.12%
    """

    if value is None or pd.isna(value):
        return "0.00%"

    return f"{value:.2f}%"


# ============================================================
# COLUMN HELPERS
# ============================================================

def get_category_column(df: pd.DataFrame) -> str | None:
    """
    Finds the best available product category column.

    Preferred:
        main_product_category_english

    Fallback:
        main_product_category
    """

    if "main_product_category_english" in df.columns:
        return "main_product_category_english"

    if "main_product_category" in df.columns:
        return "main_product_category"

    return None


def get_payment_column(df: pd.DataFrame) -> str | None:
    """
    Finds the best available payment type column.
    """

    if "primary_payment_type" in df.columns:
        return "primary_payment_type"

    if "payment_type" in df.columns:
        return "payment_type"

    return None


def get_seller_column(df: pd.DataFrame) -> str | None:
    """
    Finds the best available seller column.
    """

    if "main_seller_id" in df.columns:
        return "main_seller_id"

    if "seller_id" in df.columns:
        return "seller_id"

    return None


# ============================================================
# CHART HELPERS
# ============================================================

def apply_chart_layout(fig, height: int = 430):
    """
    Applies consistent professional formatting to Plotly charts.

    This keeps all dashboard charts visually consistent.
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
    Displays a Plotly chart in Streamlit.

    use_container_width=True makes the chart responsive.
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
    Loads master_data from marketing.db.

    This function is cached by Streamlit.
    That means Streamlit does not reload the database on every small UI action.
    """

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run `python main.py` first."
        )

    engine = create_engine(DATABASE_URL)

    query = "SELECT * FROM master_data"

    df = pd.read_sql(query, engine)

    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts date columns to datetime.

    Why:
        Streamlit filters and Plotly charts need real datetime values.
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
    Applies sidebar filters.

    Empty dropdown selections mean:
        include all values
    """

    st.sidebar.title("Filters")

    st.sidebar.caption(
        "Use filters to narrow the dashboard. Empty selections include all values."
    )

    filtered = df.copy()

    # --------------------------------------------------------
    # Date filter
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Order status filter
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Customer state filter
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Product category filter
    # --------------------------------------------------------

    category_column = get_category_column(filtered)

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

    # --------------------------------------------------------
    # Sidebar summary metrics
    # --------------------------------------------------------

    filtered_orders = (
        filtered["order_id"].nunique()
        if "order_id" in filtered.columns
        else len(filtered)
    )

    gross_payment_value = (
        filtered["payment_value"].sum()
        if "payment_value" in filtered.columns
        else 0
    )

    if {"order_status", "payment_value"}.issubset(filtered.columns):
        delivered_payment_value = filtered.loc[
            filtered["order_status"] == "delivered",
            "payment_value"
        ].sum()
    else:
        delivered_payment_value = 0

    st.sidebar.metric(
        "Filtered orders",
        f"{filtered_orders:,}"
    )

    st.sidebar.metric(
        "Filtered gross payment value",
        format_currency(gross_payment_value)
    )

    st.sidebar.metric(
        "Filtered delivered revenue",
        format_currency(delivered_payment_value)
    )

    return filtered


# ============================================================
# KPI SECTIONS
# ============================================================

def show_kpi_cards(df: pd.DataFrame):
    """
    Shows executive KPI cards.

    These are the main business health numbers.
    """

    kpis = calculate_kpis(df)

    # --------------------------------------------------------
    # Row 1: financial and order KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Gross Payment Value",
        format_currency(kpis.get("total_revenue", 0)),
        help=(
            "Sum of payment_value for selected orders, regardless of order status. "
            "Canceled orders may still have recorded payment values."
        )
    )

    col2.metric(
        "Delivered Revenue",
        format_currency(kpis.get("delivered_revenue", 0)),
        help="Revenue from delivered orders only."
    )

    col3.metric(
        "Total Orders",
        format_number(kpis.get("total_orders", 0)),
        help="Unique order_id count."
    )

    col4.metric(
        "Average Gross Order Value",
        format_currency(kpis.get("average_order_value", 0)),
        help="Gross payment value divided by total orders."
    )

    # --------------------------------------------------------
    # Row 2: customer and operational KPIs
    # --------------------------------------------------------

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Unique Customers",
        format_number(kpis.get("unique_customers", 0)),
        help="Unique customers based on customer_unique_id."
    )

    col6.metric(
        "Repeat Customer Rate",
        format_percentage(kpis.get("repeat_customer_rate", 0)),
        help="Customers with more than one order."
    )

    col7.metric(
        "Cancellation Rate",
        format_percentage(kpis.get("cancellation_rate", 0)),
        help="Canceled orders divided by total orders."
    )

    col8.metric(
        "Late Delivery Rate",
        format_percentage(kpis.get("late_delivery_rate", 0)),
        help="Orders delivered later than estimated date."
    )


def show_operations_kpis(df: pd.DataFrame):
    """
    Shows operational KPI cards.

    These KPIs explain fulfillment, cancellation, and customer experience.
    """

    kpis = calculate_kpis(df)

    # --------------------------------------------------------
    # Row 1: order status KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Delivered Orders",
        format_number(kpis.get("delivered_orders", 0)),
        help="Unique delivered orders."
    )

    col2.metric(
        "Canceled Orders",
        format_number(kpis.get("canceled_orders", 0)),
        help="Unique canceled orders."
    )

    col3.metric(
        "Unavailable Orders",
        format_number(kpis.get("unavailable_orders", 0)),
        help="Unique unavailable orders."
    )

    col4.metric(
        "Delivery Success Rate",
        format_percentage(kpis.get("delivery_success_rate", 0)),
        help="Delivered orders divided by total orders."
    )

    # --------------------------------------------------------
    # Row 2: operational performance KPIs
    # --------------------------------------------------------

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Canceled Gross Payment Value",
        format_currency(kpis.get("canceled_gross_payment_value", 0)),
        help="Recorded payment_value for canceled orders."
    )

    col6.metric(
        "Average Delivery Time",
        f"{kpis.get('average_delivery_time_days', 0):.1f} days",
        help="Average days from purchase to delivery."
    )

    col7.metric(
        "Average Review Score",
        f"{kpis.get('average_review_score', 0):.2f}",
        help="Average customer review score."
    )

    col8.metric(
        "Orders per Customer",
        f"{kpis.get('orders_per_customer', 0):.2f}",
        help="Average orders per unique customer."
    )


# ============================================================
# CHARTS
# ============================================================

def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates monthly gross payment value and order count.

    Output columns:
        order_month
        gross_payment_value
        orders
    """

    required = {
        "order_purchase_timestamp",
        "payment_value",
        "order_id"
    }

    if not required.issubset(df.columns):
        return pd.DataFrame()

    monthly_df = df.dropna(
        subset=["order_purchase_timestamp"]
    ).copy()

    if monthly_df.empty:
        return pd.DataFrame()

    monthly_df["order_month"] = (
        monthly_df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        monthly_df
        .groupby("order_month")
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    return monthly


def chart_monthly_revenue(df: pd.DataFrame):
    """
    Shows monthly gross payment value trend.
    """

    monthly = get_monthly_summary(df)

    if monthly.empty:
        st.warning("Monthly gross payment value chart skipped.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["order_month"],
            y=monthly["gross_payment_value"],
            mode="lines+markers",
            name="Gross Payment Value",
            line=dict(width=3, color="#2563EB"),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.12)",
            hovertemplate=(
                "Month: %{x}<br>"
                "Gross Payment Value: %{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Monthly Gross Payment Value Trend",
        xaxis_title="Month",
        yaxis_title="Gross Payment Value"
    )

    fig = apply_chart_layout(fig, height=460)

    show_chart(fig)


def chart_revenue_vs_orders(df: pd.DataFrame):
    """
    Shows gross payment value and order volume together.
    """

    monthly = get_monthly_summary(df)

    if monthly.empty:
        st.warning("Gross payment value vs orders chart skipped.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=monthly["order_month"],
            y=monthly["gross_payment_value"],
            name="Gross Payment Value",
            marker_color="#93C5FD",
            yaxis="y1",
            hovertemplate="Gross Payment Value: %{y:,.0f}<extra></extra>"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["order_month"],
            y=monthly["orders"],
            name="Orders",
            mode="lines+markers",
            line=dict(width=3, color="#0F172A"),
            yaxis="y2",
            hovertemplate="Orders: %{y:,.0f}<extra></extra>"
        )
    )

    fig.update_layout(
        title="Gross Payment Value and Order Volume",
        xaxis=dict(title="Month"),
        yaxis=dict(title="Gross Payment Value"),
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
    Shows top product categories by gross payment value.
    """

    category_column = get_category_column(df)

    if category_column is None or "payment_value" not in df.columns:
        st.warning("Category chart skipped.")
        return

    categories = (
        df.dropna(subset=[category_column])
        .groupby(category_column)
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .sort_values("gross_payment_value", ascending=False)
        .head(12)
        .reset_index()
    )

    if categories.empty:
        st.warning("No category data available.")
        return

    fig = px.bar(
        categories.sort_values("gross_payment_value"),
        x="gross_payment_value",
        y=category_column,
        orientation="h",
        title="Top Product Categories by Gross Payment Value",
        text="gross_payment_value",
        hover_data=["orders"],
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Gross Payment Value",
        yaxis_title="Product Category"
    )

    fig = apply_chart_layout(fig, height=560)

    show_chart(fig)


def chart_order_status(df: pd.DataFrame):
    """
    Shows order status distribution.
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

    if status.empty:
        st.warning("No order status data available.")
        return

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
    Shows payment method share.
    """

    payment_column = get_payment_column(df)

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

    if payment.empty:
        st.warning("No payment method data available.")
        return

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
    Shows number of orders per customer.
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

    if customer_orders.empty:
        st.warning("No customer frequency data available.")
        return

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
    Shows gross payment value by customer state.
    """

    required = {"customer_state", "payment_value", "order_id"}

    if not required.issubset(df.columns):
        st.warning("Customer state chart skipped.")
        return

    states = (
        df.dropna(subset=["customer_state"])
        .groupby("customer_state")
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .sort_values("gross_payment_value", ascending=False)
        .reset_index()
    )

    if states.empty:
        st.warning("No customer state data available.")
        return

    fig = px.bar(
        states,
        x="customer_state",
        y="gross_payment_value",
        title="Gross Payment Value by Customer State",
        text="gross_payment_value",
        hover_data=["orders"],
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Customer State",
        yaxis_title="Gross Payment Value"
    )

    fig = apply_chart_layout(fig, height=470)

    show_chart(fig)


def chart_delivery_delay(df: pd.DataFrame):
    """
    Shows delivery delay distribution.
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
    Shows top sellers by gross payment value.
    """

    seller_column = get_seller_column(df)

    if seller_column is None or "payment_value" not in df.columns:
        st.warning("Seller chart skipped.")
        return

    sellers = (
        df.dropna(subset=[seller_column])
        .groupby(seller_column)
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique")
        )
        .sort_values("gross_payment_value", ascending=False)
        .head(12)
        .reset_index()
    )

    if sellers.empty:
        st.warning("No seller data available.")
        return

    fig = px.bar(
        sellers.sort_values("gross_payment_value"),
        x="gross_payment_value",
        y=seller_column,
        orientation="h",
        title="Top Sellers by Gross Payment Value",
        text="gross_payment_value",
        hover_data=["orders"],
        color_discrete_sequence=["#2563EB"]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Gross Payment Value",
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

    gross_payment_value = (
        df["payment_value"].sum()
        if "payment_value" in df.columns
        else None
    )

    if {"order_status", "payment_value"}.issubset(df.columns):
        delivered_revenue = df.loc[
            df["order_status"] == "delivered",
            "payment_value"
        ].sum()
    else:
        delivered_revenue = None

    col1, col2, col3, col4 = st.columns(4)

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

    col4.metric(
        "Gross payment value",
        format_currency(gross_payment_value) if gross_payment_value is not None else "N/A"
    )

    st.caption(
        "Note: Gross payment value may include canceled orders with recorded payment_value. "
        "Delivered revenue only counts delivered orders."
    )

    if delivered_revenue is not None:
        st.metric(
            "Delivered revenue",
            format_currency(delivered_revenue)
        )


# ============================================================
# MAIN APP
# ============================================================

def main():
    """
    Runs the Streamlit dashboard.
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
            <b>Gross Payment Value</b> is the sum of recorded payment_value for selected orders,
            regardless of status.
            <b>Delivered Revenue</b> only counts delivered orders.
            Payments and items are aggregated before merging to prevent inflated metrics.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Gross Value",
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
        st.markdown(
            '<div class="section-title">Operational Health</div>',
            unsafe_allow_html=True
        )

        show_operations_kpis(filtered_df)

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