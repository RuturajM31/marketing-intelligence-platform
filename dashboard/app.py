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
import sqlite3
import subprocess
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
    page_title="Ecommerce Intelligence",
    page_icon="📈",
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

# V4_REAL_PORTFOLIO_SHELL

st.markdown(
    """
    <style>
        :root {
            --bg: #F6F7FB;
            --card: #FFFFFF;
            --ink: #111827;
            --muted: #4B5563;
            --line: #E5E7EB;
            --brand: #7C3AED;
            --amber: #B45309;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(124,58,237,0.10), transparent 34rem),
                linear-gradient(180deg, #F9FAFB 0%, #F3F4F6 100%) !important;
        }

        .block-container {
            max-width: 1500px !important;
            padding-top: 1.15rem !important;
            padding-bottom: 2.5rem !important;
        }

        .main-header {
            background: linear-gradient(135deg, #111827 0%, #312E81 55%, #7C2D12 100%) !important;
            border: 0 !important;
            border-radius: 30px !important;
            padding: 2.1rem 2.3rem !important;
            margin-bottom: 1.35rem !important;
            box-shadow: 0 24px 70px rgba(17,24,39,0.24) !important;
        }

        .main-title {
            color: #FFFFFF !important;
            font-size: 2.8rem !important;
            line-height: 1.04 !important;
            font-weight: 950 !important;
            letter-spacing: -0.055em !important;
            margin-bottom: 0.55rem !important;
        }

        .main-subtitle {
            color: #F3F4F6 !important;
            font-size: 1.06rem !important;
            max-width: 980px !important;
            line-height: 1.62 !important;
        }

        .main-header::after {
            content: "";
            display: inline-block;
            margin-top: 1.1rem;
            background: rgba(255,255,255,0.13);
            border: 1px solid rgba(255,255,255,0.24);
            color: #FFFFFF;
            border-radius: 999px;
            padding: 0.52rem 0.85rem;
            font-size: 0.9rem;
            font-weight: 850;
        }

        section[data-testid="stSidebar"] {
            background: #FFFFFF !important;
            border-right: 1px solid var(--line) !important;
        }

        section[data-testid="stSidebar"] * {
            color: var(--ink) !important;
        }

        .sidebar-brand {
            background: linear-gradient(135deg, #111827, #312E81);
            border-radius: 20px;
            padding: 1.05rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 32px rgba(17,24,39,0.18);
        }

        .sidebar-brand-title {
            color: #FFFFFF !important;
            font-size: 1.04rem;
            font-weight: 950;
            letter-spacing: -0.02em;
            margin-bottom: 0.35rem;
        }

        .sidebar-brand-subtitle {
            color: #E5E7EB !important;
            font-size: 0.82rem;
            line-height: 1.45;
        }

        div[data-testid="stMetric"] {
            background: var(--card) !important;
            border: 1px solid var(--line) !important;
            border-radius: 22px !important;
            padding: 1.12rem !important;
            box-shadow: 0 14px 34px rgba(17,24,39,0.075) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #374151 !important;
            font-weight: 850 !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--ink) !important;
            font-size: 1.72rem !important;
            font-weight: 950 !important;
            letter-spacing: -0.035em !important;
        }

        div[data-testid="stTabs"] [role="tablist"] {
            gap: 0.45rem !important;
            flex-wrap: wrap !important;
            border-bottom: 0 !important;
        }

        button[data-baseweb="tab"] {
            background: #FFFFFF !important;
            color: var(--ink) !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 999px !important;
            padding: 0.62rem 1rem !important;
            font-weight: 850 !important;
            box-shadow: 0 8px 18px rgba(17,24,39,0.05) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: #111827 !important;
            color: #FFFFFF !important;
            border-color: #111827 !important;
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF !important;
            border: 1px solid var(--line) !important;
            border-radius: 24px !important;
            padding: 1.1rem !important;
            box-shadow: 0 16px 38px rgba(17,24,39,0.08) !important;
            margin-bottom: 1.35rem !important;
        }

        .grain-card {
            background: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-left: 6px solid var(--brand) !important;
            border-radius: 22px !important;
            padding: 1.05rem 1.15rem !important;
            box-shadow: 0 12px 30px rgba(17,24,39,0.06) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] .sidebar-brand,
        section[data-testid="stSidebar"] .sidebar-brand * {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] .sidebar-brand-subtitle {
            color: #E5E7EB !important;
        }

        .section-brief {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-left: 6px solid #7C3AED;
            border-radius: 22px;
            padding: 1.05rem 1.15rem;
            margin: 1rem 0 1.25rem 0;
            box-shadow: 0 12px 30px rgba(17,24,39,0.06);
        }

        .section-brief-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 950;
            margin-bottom: 0.35rem;
        }

        .section-brief-text {
            color: #4B5563;
            font-size: 0.95rem;
            line-height: 1.6;
        }
    </style>
    """,
    unsafe_allow_html=True
)



# V4_FINAL_FRIDAY_POLISH_CSS

st.markdown(
    """
    <style>
        .section-title {
            color: #111827;
            font-size: 1.38rem;
            font-weight: 950;
            letter-spacing: -0.02em;
            margin-top: 0.4rem;
            margin-bottom: 0.9rem;
        }

        .section-brief {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-left: 6px solid #7C3AED;
            border-radius: 22px;
            padding: 1.05rem 1.15rem;
            margin: 1rem 0 1.25rem 0;
            box-shadow: 0 12px 30px rgba(17,24,39,0.06);
        }

        .section-brief-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 950;
            margin-bottom: 0.35rem;
        }

        .section-brief-text {
            color: #4B5563;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 22px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 14px 34px rgba(17,24,39,0.075);
            min-height: 142px;
            margin-bottom: 1rem;
        }

        .metric-topline {
            display: flex;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.78rem;
        }

        .metric-label {
            color: #4B5563;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.055em;
            text-transform: uppercase;
        }

        .metric-badge {
            border-radius: 999px;
            padding: 0.22rem 0.55rem;
            font-size: 0.68rem;
            font-weight: 900;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .badge-good {
            background: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
        }

        .badge-watch {
            background: #FFFBEB;
            color: #B45309;
            border: 1px solid #FDE68A;
        }

        .badge-risk {
            background: #FEF2F2;
            color: #B91C1C;
            border: 1px solid #FECACA;
        }

        .badge-info {
            background: #EEF2FF;
            color: #4338CA;
            border: 1px solid #C7D2FE;
        }

        .metric-value {
            color: #111827;
            font-size: 2rem;
            line-height: 1.05;
            font-weight: 950;
            letter-spacing: -0.045em;
            margin-bottom: 0.55rem;
        }

        .metric-note {
            color: #4B5563;
            font-size: 0.86rem;
            line-height: 1.45;
        }
    </style>
    """,
    unsafe_allow_html=True
)


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
    Renders Plotly charts with the final dark theme.

    Presentation only. It does not modify data, filters, joins, aggregations,
    KPI formulas, or business logic.
    """

    dark_bg = "#0B1220"
    panel_bg = "#111827"
    text = "#F8FAFC"
    muted = "#CBD5E1"
    grid = "#334155"

    fig.update_layout(
        paper_bgcolor=panel_bg,
        plot_bgcolor=dark_bg,
        font=dict(family="Arial", size=15, color=text),
        hoverlabel=dict(bgcolor="#020617", font_size=14, font_color=text, bordercolor="#475569"),
        margin=dict(l=62, r=50, t=100, b=78),
        title=dict(font=dict(size=27, color=text, family="Arial Black")),
    )

    fig.update_xaxes(
        title_font=dict(size=15, color=text),
        tickfont=dict(size=13, color=muted),
        linecolor="#64748B",
        linewidth=1,
        gridcolor=grid,
        zerolinecolor="#475569",
        automargin=True,
    )

    fig.update_yaxes(
        title_font=dict(size=15, color=text),
        tickfont=dict(size=13, color=muted),
        linecolor="#64748B",
        linewidth=1,
        gridcolor=grid,
        zerolinecolor="#475569",
        automargin=True,
    )

    fig.update_layout(
        legend=dict(
            font=dict(size=13, color=text),
            bgcolor="rgba(15,23,42,0)",
        )
    )

    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color=muted, size=12),
            title_font=dict(color=text, size=13),
            outlinecolor="#475569",
        )
    )

    if hasattr(fig.layout, "yaxis2"):
        fig.update_layout(
            yaxis2=dict(
                titlefont=dict(color=text, size=15),
                tickfont=dict(color=muted, size=13),
                gridcolor=grid,
                zerolinecolor="#475569",
            )
        )

    if hasattr(fig.layout, "scene"):
        fig.update_layout(
            scene=dict(
                bgcolor=dark_bg,
                xaxis=dict(backgroundcolor=dark_bg, gridcolor="#334155", color=text, zerolinecolor="#475569"),
                yaxis=dict(backgroundcolor=dark_bg, gridcolor="#334155", color=text, zerolinecolor="#475569"),
                zaxis=dict(backgroundcolor=dark_bg, gridcolor="#334155", color=text, zerolinecolor="#475569"),
            )
        )

    for trace in fig.data:
        if hasattr(trace, "textfont"):
            try:
                trace.textfont.color = text
            except Exception:
                pass

        if hasattr(trace, "marker") and hasattr(trace.marker, "colorbar"):
            try:
                trace.marker.colorbar.tickfont = dict(color=muted, size=12)
                trace.marker.colorbar.title = dict(font=dict(color=text, size=13))
                trace.marker.colorbar.outlinecolor = "#475569"
            except Exception:
                pass

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


def _database_is_ready() -> bool:
    """Return True only when marketing.db has a populated master_data table.

    The check prevents Streamlit from rebuilding the database on every rerun.
    It also rejects incomplete SQLite files left behind by an interrupted
    first-start pipeline.
    """
    if not DB_PATH.is_file():
        return False

    try:
        with sqlite3.connect(DB_PATH) as connection:
            table_exists = connection.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = 'master_data'
                LIMIT 1
                """
            ).fetchone()

            if table_exists is None:
                return False

            row_count = connection.execute(
                "SELECT COUNT(*) FROM master_data"
            ).fetchone()[0]

        return row_count > 0
    except sqlite3.Error:
        return False


def _final_output_lines(output: str, limit: int = 30) -> str:
    """Keep only the final diagnostic lines from pipeline output."""
    lines = (output or "").splitlines()
    return "\n".join(lines[-limit:])


@st.cache_resource(show_spinner=False)
def ensure_database_ready() -> bool:
    """Create and validate marketing.db once per Streamlit server process.

    Streamlit Community Cloud starts from a clean repository checkout, while
    generated databases and raw datasets are intentionally excluded from Git.
    When the database is absent or invalid, the existing main.py pipeline is
    run with the same Python interpreter used by Streamlit.
    """
    if _database_is_ready():
        return True

    pipeline_path = PROJECT_ROOT / "main.py"
    if not pipeline_path.is_file():
        raise RuntimeError(f"Pipeline entry point not found: {pipeline_path}")

    try:
        result = subprocess.run(
            [sys.executable, str(pipeline_path)],
            cwd=PROJECT_ROOT,
            shell=False,
            capture_output=True,
            text=True,
            check=False,
            timeout=900,
        )
    except subprocess.TimeoutExpired as error:
        stdout_tail = _final_output_lines(error.stdout or "")
        stderr_tail = _final_output_lines(error.stderr or "")
        raise RuntimeError(
            "Analytics database preparation timed out after 900 seconds.\n"
            f"Final stdout:\n{stdout_tail or '[empty]'}\n"
            f"Final stderr:\n{stderr_tail or '[empty]'}"
        ) from error

    if result.returncode != 0:
        raise RuntimeError(
            "Analytics database preparation failed.\n"
            f"Return code: {result.returncode}\n"
            f"Final stdout:\n"
            f"{_final_output_lines(result.stdout) or '[empty]'}\n"
            f"Final stderr:\n"
            f"{_final_output_lines(result.stderr) or '[empty]'}"
        )

    if not _database_is_ready():
        raise RuntimeError(
            "The data pipeline finished successfully, but marketing.db does "
            "not contain a populated master_data table."
        )

    return True


@st.cache_data(show_spinner=False)
def load_master_data() -> pd.DataFrame:
    """Load the validated master_data table without repeating startup work."""
    with st.spinner(
        "Preparing the analytics database. First startup may take a few minutes..."
    ):
        ensure_database_ready()

    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM master_data"

    try:
        return pd.read_sql(query, engine)
    finally:
        engine.dispose()


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

    st.sidebar.markdown("""
<div class="sidebar-brand">
  <div class="sidebar-brand-title">Ecommerce Intelligence</div>
  <div class="sidebar-brand-subtitle">
    Performance control for revenue, customers, operations, sellers, payments, and data quality.
  </div>
</div>
""", unsafe_allow_html=True)


    st.sidebar.markdown("### Command Filters")

    st.sidebar.caption(
        "Filter the dashboard. Empty selections include all values."
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



def section_brief(title: str, body: str):
    """
    Renders a short business explanation above a dashboard section.

    This is presentation only. It does not alter filters, source data, or KPI logic.
    """
    st.markdown(
        f"""
        <div class="section-brief">
            <div class="section-brief-title">{title}</div>
            <div class="section-brief-text">{body}</div>
        </div>
        """,
        unsafe_allow_html=True
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
# V5 VERIFIED VISUAL RICH APP

# V5_FINAL_VISUAL_POLISH_CSS

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            color: #0B1220 !important;
        }

        .block-container {
            max-width: 1580px !important;
        }

        .main-header {
            box-shadow: 0 30px 86px rgba(15,23,42,0.30) !important;
        }

        .section-title {
            color: #0B1220 !important;
            font-size: 1.58rem !important;
            font-weight: 950 !important;
        }

        .section-brief, .grain-card {
            color: #172033 !important;
            font-size: 0.98rem !important;
            border-left: 7px solid #4F46E5 !important;
            box-shadow: 0 16px 40px rgba(15,23,42,0.10) !important;
        }

        .section-brief-title {
            color: #0B1220 !important;
            font-weight: 950 !important;
        }

        .section-brief-text {
            color: #1F2937 !important;
            font-weight: 650 !important;
        }

        .metric-card {
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 16px 38px rgba(15,23,42,0.12) !important;
        }

        .metric-label {
            color: #1E293B !important;
            font-weight: 950 !important;
        }

        .metric-value {
            color: #020617 !important;
            font-weight: 950 !important;
        }

        .metric-note {
            color: #1F2937 !important;
            font-weight: 650 !important;
        }

        div[data-testid="stPlotlyChart"] {
            border: 1px solid #CBD5E1 !important;
            border-radius: 28px !important;
            box-shadow: 0 20px 52px rgba(15,23,42,0.12) !important;
            padding: 1.25rem !important;
            background: #FFFFFF !important;
        }

        div[role="radiogroup"] label p {
            color: #0B1220 !important;
            font-weight: 800 !important;
        }

        section[data-testid="stSidebar"] * {
            color: #0B1220 !important;
            font-weight: 650 !important;
        }

        section[data-testid="stSidebar"] .sidebar-brand,
        section[data-testid="stSidebar"] .sidebar-brand * {
            color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(124,58,237,0.14), transparent 36rem),
                radial-gradient(circle at top right, rgba(15,118,110,0.10), transparent 34rem),
                linear-gradient(180deg, #F9FAFB 0%, #F3F4F6 100%) !important;
        }

        .block-container {
            max-width: 1540px !important;
            padding-top: 1.05rem !important;
            padding-bottom: 3rem !important;
        }

        .main-header {
            background: linear-gradient(135deg, #111827 0%, #312E81 52%, #7C2D12 100%) !important;
            border-radius: 30px !important;
            padding: 2.2rem 2.4rem !important;
            margin-bottom: 1.35rem !important;
            box-shadow: 0 26px 76px rgba(17,24,39,0.26) !important;
        }

        .main-title {
            color: #FFFFFF !important;
            font-size: 2.9rem !important;
            line-height: 1.04 !important;
            font-weight: 950 !important;
            letter-spacing: -0.055em !important;
            margin-bottom: 0.55rem !important;
        }

        .main-subtitle {
            color: #F3F4F6 !important;
            font-size: 1.06rem !important;
            max-width: 1080px !important;
            line-height: 1.62 !important;
        }

        .main-header::after {
            content: "";
            display: inline-block;
            margin-top: 1.1rem;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.26);
            color: #FFFFFF;
            border-radius: 999px;
            padding: 0.52rem 0.85rem;
            font-size: 0.9rem;
            font-weight: 850;
        }

        .section-title {
            color: #111827;
            font-size: 1.44rem;
            font-weight: 950;
            letter-spacing: -0.02em;
            margin-top: 0.4rem;
            margin-bottom: 0.9rem;
        }

        .section-brief, .grain-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-left: 6px solid #7C3AED;
            border-radius: 22px;
            padding: 1.05rem 1.15rem;
            margin: 1rem 0 1.25rem 0;
            box-shadow: 0 14px 34px rgba(17,24,39,0.07);
            color: #4B5563;
            line-height: 1.62;
        }

        .section-brief-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 950;
            margin-bottom: 0.35rem;
        }

        .section-brief-text {
            color: #4B5563;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 22px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 14px 34px rgba(17,24,39,0.08);
            min-height: 142px;
            margin-bottom: 1rem;
        }

        .metric-topline {
            display: flex;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.78rem;
        }

        .metric-label {
            color: #4B5563;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.055em;
            text-transform: uppercase;
        }

        .metric-badge {
            border-radius: 999px;
            padding: 0.22rem 0.55rem;
            font-size: 0.68rem;
            font-weight: 900;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .badge-good { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
        .badge-watch { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
        .badge-risk { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
        .badge-info { background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; }

        .metric-value {
            color: #111827;
            font-size: 2rem;
            line-height: 1.05;
            font-weight: 950;
            letter-spacing: -0.045em;
            margin-bottom: 0.55rem;
        }

        .metric-note {
            color: #4B5563;
            font-size: 0.86rem;
            line-height: 1.45;
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 26px !important;
            padding: 1.1rem !important;
            box-shadow: 0 18px 44px rgba(17,24,39,0.09) !important;
            margin-bottom: 1.35rem !important;
        }

        div[role="radiogroup"] {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 999px;
            padding: 0.35rem;
            box-shadow: 0 12px 30px rgba(17,24,39,0.06);
            margin-bottom: 1.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def v5_safe_numeric(series: pd.Series) -> pd.Series:
    """
    Converts a Series to numeric values that Plotly can safely render.
    """

    return pd.to_numeric(series, errors="coerce").replace([float("inf"), float("-inf")], 0).fillna(0)


def v5_short_label(value, limit: int = 28) -> str:
    """
    Shortens long labels to keep charts readable.
    """

    label = str(value)

    if len(label) <= limit:
        return label

    return label[: limit - 3] + "..."


def v5_apply_layout(fig, height: int = 580, legend: bool = True):
    """
    Applies the final dark Plotly layout.

    Presentation only. It does not modify source data, filters, KPI formulas,
    or aggregation logic.
    """

    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=62, r=52, t=102, b=78),
        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(size=27, color="#F8FAFC", family="Arial Black"),
        ),
        font=dict(family="Arial", size=15, color="#F8FAFC"),
        paper_bgcolor="#111827",
        plot_bgcolor="#0B1220",
        hoverlabel=dict(bgcolor="#020617", font_size=14, font_color="#F8FAFC", bordercolor="#475569"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(size=13, color="#F8FAFC"),
            bgcolor="rgba(15,23,42,0)",
        ) if legend else None,
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#64748B",
        linewidth=1,
        title_font=dict(size=15, color="#F8FAFC"),
        tickfont=dict(size=13, color="#CBD5E1"),
        automargin=True,
    )

    fig.update_yaxes(
        gridcolor="#334155",
        zeroline=False,
        linecolor="#64748B",
        linewidth=1,
        title_font=dict(size=15, color="#F8FAFC"),
        tickfont=dict(size=13, color="#CBD5E1"),
        automargin=True,
    )

    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color="#CBD5E1", size=12),
            title_font=dict(color="#F8FAFC", size=13),
            outlinecolor="#475569",
        )
    )

    if hasattr(fig.layout, "yaxis2"):
        fig.update_layout(
            yaxis2=dict(
                titlefont=dict(color="#F8FAFC", size=15),
                tickfont=dict(color="#CBD5E1", size=13),
                gridcolor="#334155",
                zerolinecolor="#475569",
            )
        )

    return fig

def v5_section_brief(title: str, body: str):
    """
    Renders a business explanation card.
    """

    st.markdown(
        f"""
        <div class="section-brief">
            <div class="section-brief-title">{title}</div>
            <div class="section-brief-text">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def v5_metric_card(label: str, value: str, note: str, badge: str = "INFO", badge_type: str = "info"):
    """
    Renders a enterprise-grade KPI card.
    """

    st.markdown(
        f"""
        <div class="metric-card" title="KPI card: real monthly sparkline based on the current filters.">
            <div class="metric-topline">
                <div class="metric-label">{label}</div>
                <div class="metric-badge badge-{badge_type}">{badge}</div>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def v5_show_executive_kpis(df: pd.DataFrame):
    """
    Shows executive KPI cards from calculate_kpis(df).
    """

    kpis = calculate_kpis(df)

    gross = kpis.get("total_revenue", 0)
    delivered = kpis.get("delivered_revenue", 0)
    orders = kpis.get("total_orders", 0)
    aov = kpis.get("average_order_value", 0)
    customers = kpis.get("unique_customers", 0)
    repeat_rate = kpis.get("repeat_customer_rate", 0)
    cancel_rate = kpis.get("cancellation_rate", 0)
    late_rate = kpis.get("late_delivery_rate", 0)

    leakage = max(gross - delivered, 0)
    delivered_share = delivered / gross * 100 if gross else 0

    cards = [
        ("Gross payment value", format_currency(gross), "Recorded demand value across selected orders.", "Revenue", "info"),
        ("Delivered revenue", format_currency(delivered), f"{format_percentage(delivered_share)} of gross value reached delivered status.", "Quality", "good"),
        ("Revenue leakage", format_currency(leakage), "Gap between gross value and delivered revenue.", "Watch", "watch"),
        ("Total orders", format_number(orders), "Unique order_id count after active filters.", "Volume", "info"),
        ("Average gross order value", format_currency(aov), "Gross payment value divided by total orders.", "AOV", "info"),
        ("Unique customers", format_number(customers), "Unique customers based on customer_unique_id.", "Audience", "info"),
        ("Repeat customer rate", format_percentage(repeat_rate), "Retention and lifecycle marketing signal.", "Watch" if repeat_rate < 10 else "Good", "watch" if repeat_rate < 10 else "good"),
        ("Late delivery rate", format_percentage(late_rate), f"Cancellation rate is {format_percentage(cancel_rate)}.", "Risk" if late_rate >= 5 else "Good", "risk" if late_rate >= 5 else "good"),
    ]

    for row_start in [0, 4]:
        cols = st.columns(4)

        for col, card in zip(cols, cards[row_start: row_start + 4]):
            with col:
                v5_metric_card(*card)


def v5_show_operations_kpis(df: pd.DataFrame):
    """
    Shows operational KPI cards from calculate_kpis(df).
    """

    kpis = calculate_kpis(df)

    cards = [
        ("Delivered orders", format_number(kpis.get("delivered_orders", 0)), "Orders completed with delivered status.", "Success", "good"),
        ("Canceled orders", format_number(kpis.get("canceled_orders", 0)), "Canceled order count after active filters.", "Risk" if kpis.get("canceled_orders", 0) else "Good", "risk" if kpis.get("canceled_orders", 0) else "good"),
        ("Unavailable orders", format_number(kpis.get("unavailable_orders", 0)), "Orders unavailable after purchase flow.", "Watch", "watch"),
        ("Delivery success rate", format_percentage(kpis.get("delivery_success_rate", 0)), "Delivered orders divided by total orders.", "Good" if kpis.get("delivery_success_rate", 0) >= 95 else "Watch", "good" if kpis.get("delivery_success_rate", 0) >= 95 else "watch"),
        ("Canceled gross value", format_currency(kpis.get("canceled_gross_payment_value", 0)), "Recorded payment value tied to canceled orders.", "Leakage", "watch"),
        ("Average delivery time", f"{kpis.get('average_delivery_time_days', 0):.1f} days", "Average days from purchase to delivery.", "Speed", "info"),
        ("Average review score", f"{kpis.get('average_review_score', 0):.2f}", "Customer review signal for delivered experience.", "Good" if kpis.get("average_review_score", 0) >= 4 else "Watch", "good" if kpis.get("average_review_score", 0) >= 4 else "watch"),
        ("Orders per customer", f"{kpis.get('orders_per_customer', 0):.2f}", "Average orders per unique customer.", "Retention", "info"),
    ]

    for row_start in [0, 4]:
        cols = st.columns(4)

        for col, card in zip(cols, cards[row_start: row_start + 4]):
            with col:
                v5_metric_card(*card)


def v5_chart_revenue_waterfall(df: pd.DataFrame):
    """
    Replaces the old waterfall with a dark revenue realization bridge.

    The function name is preserved because main() already calls it. The visual
    is no longer a waterfall chart.
    """

    if not {"payment_value", "order_status"}.issubset(df.columns):
        st.warning("Revenue realization bridge skipped.")
        return

    gross = float(df["payment_value"].sum())
    delivered = float(df.loc[df["order_status"] == "delivered", "payment_value"].sum())
    leakage = max(gross - delivered, 0)

    delivered_pct = delivered / gross * 100 if gross else 0
    leakage_pct = leakage / gross * 100 if gross else 0

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=["Gross payment value"],
            x=[delivered],
            orientation="h",
            name="Delivered revenue",
            marker=dict(color="#14B8A6", line=dict(color="#5EEAD4", width=1)),
            text=[f"{format_currency(delivered)} · {delivered_pct:.1f}% delivered"],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=16, color="#020617"),
            hovertemplate="Delivered revenue: %{x:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            y=["Gross payment value"],
            x=[leakage],
            orientation="h",
            name="Non-delivered leakage",
            marker=dict(color="#F43F5E", line=dict(color="#FDA4AF", width=1)),
            text=[f"{format_currency(leakage)} · {leakage_pct:.1f}% leakage"],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=16, color="#FFFFFF"),
            hovertemplate="Non-delivered leakage: %{x:,.0f}<extra></extra>",
        )
    )

    fig.add_annotation(
        x=delivered,
        y="Gross payment value",
        text=f"Gross value: {format_currency(gross)}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#CBD5E1",
        ax=40,
        ay=-70,
        font=dict(size=16, color="#F8FAFC"),
        bgcolor="rgba(15,23,42,0.95)",
        bordercolor="#475569",
        borderpad=8,
    )

    fig.update_layout(
        title="Revenue Realization Bridge",
        xaxis_title="Payment Value",
        yaxis_title="",
        barmode="stack",
        bargap=0.42,
        annotations=[
            *fig.layout.annotations,
            dict(
                x=delivered / 2 if delivered else 0,
                y=0.42,
                xref="x",
                yref="paper",
                text="Delivered revenue",
                showarrow=False,
                font=dict(size=15, color="#5EEAD4"),
            ),
            dict(
                x=delivered + leakage / 2 if leakage else delivered,
                y=0.42,
                xref="x",
                yref="paper",
                text="Leakage / non-delivered",
                showarrow=False,
                font=dict(size=15, color="#FDA4AF"),
            ),
        ],
    )

    fig.update_xaxes(range=[0, gross * 1.08 if gross else 1])
    show_chart(v5_apply_layout(fig, height=430))

def v5_chart_monthly_revenue_combo(df: pd.DataFrame):
    """
    Shows gross value, delivered revenue, and orders by month with clearer styling.
    """

    if not {"order_purchase_timestamp", "payment_value", "order_id"}.issubset(df.columns):
        st.warning("Monthly combo skipped.")
        return

    work = df.dropna(subset=["order_purchase_timestamp"]).copy()

    if work.empty:
        st.warning("No monthly revenue data available.")
        return

    work["order_month"] = work["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        work.groupby("order_month")
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )

    if "order_status" in work.columns:
        delivered = (
            work[work["order_status"] == "delivered"]
            .groupby("order_month")["payment_value"]
            .sum()
            .rename("delivered_revenue")
            .reset_index()
        )
        monthly = monthly.merge(delivered, on="order_month", how="left")
        monthly["delivered_revenue"] = monthly["delivered_revenue"].fillna(0)
    else:
        monthly["delivered_revenue"] = monthly["gross_payment_value"]

    monthly = monthly.sort_values("order_month")
    monthly["month_label"] = monthly["order_month"].dt.strftime("%b %Y")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=monthly["month_label"],
            y=monthly["gross_payment_value"],
            name="Gross payment value",
            marker=dict(color="#4F46E5", line=dict(color="#312E81", width=1)),
            opacity=0.90,
            hovertemplate="Month: %{x}<br>Gross value: %{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["month_label"],
            y=monthly["delivered_revenue"],
            name="Delivered revenue",
            mode="lines+markers",
            line=dict(color="#047857", width=5),
            marker=dict(size=9, color="#047857", line=dict(color="#FFFFFF", width=1)),
            hovertemplate="Month: %{x}<br>Delivered revenue: %{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["month_label"],
            y=monthly["orders"],
            name="Orders",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#92400E", width=4, dash="dot"),
            marker=dict(size=7, color="#92400E"),
            hovertemplate="Month: %{x}<br>Orders: %{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Monthly Revenue Momentum",
        xaxis_title="Month",
        yaxis_title="Payment Value",
        yaxis2=dict(
            title="Orders",
            overlaying="y",
            side="right",
            showgrid=False,
            titlefont=dict(color="#0B1220", size=15),
            tickfont=dict(color="#0B1220", size=13),
        ),
        bargap=0.18,
    )

    fig = v5_apply_layout(fig, height=640)
    fig.update_xaxes(tickangle=-35)
    show_chart(fig)

def v5_chart_state_category_heatmap(df: pd.DataFrame):
    """
    Shows revenue concentration by state and product category.
    """

    category_column = get_category_column(df)

    if category_column is None or not {"customer_state", "payment_value"}.issubset(df.columns):
        st.warning("State/category heatmap skipped.")
        return

    work = df.dropna(subset=["customer_state", category_column]).copy()

    if work.empty:
        st.warning("No heatmap data available.")
        return

    top_states = work.groupby("customer_state")["payment_value"].sum().sort_values(ascending=False).head(12).index
    top_categories = work.groupby(category_column)["payment_value"].sum().sort_values(ascending=False).head(10).index

    work = work[work["customer_state"].isin(top_states) & work[category_column].isin(top_categories)]

    pivot = work.pivot_table(
        index="customer_state",
        columns=category_column,
        values="payment_value",
        aggfunc="sum",
        fill_value=0,
    )

    if pivot.empty:
        st.warning("No heatmap data available.")
        return

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[v5_short_label(x, 24) for x in pivot.columns],
            y=list(pivot.index),
            colorscale="Viridis",
            colorbar=dict(title="Gross value"),
            hovertemplate="State: %{y}<br>Category: %{x}<br>Gross value: %{z:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(title="State x Category Revenue Heatmap", xaxis_title="Product Category", yaxis_title="Customer State")
    fig = v5_apply_layout(fig, height=660, legend=False)
    fig.update_xaxes(tickangle=-35)
    show_chart(fig)


def v5_chart_product_treemap(df: pd.DataFrame):
    """
    Shows category revenue concentration.
    """

    category_column = get_category_column(df)

    if category_column is None or not {"payment_value", "order_id"}.issubset(df.columns):
        st.warning("Product treemap skipped.")
        return

    categories = (
        df.dropna(subset=[category_column])
        .groupby(category_column)
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("gross_payment_value", ascending=False)
        .head(28)
        .reset_index()
    )

    if categories.empty:
        st.warning("No treemap data available.")
        return

    categories["category_short"] = categories[category_column].map(lambda value: v5_short_label(value, 34))

    fig = px.treemap(
        categories,
        path=["category_short"],
        values="gross_payment_value",
        color="orders",
        color_continuous_scale="Viridis",
        title="Product Category Revenue Concentration",
        hover_data={"orders": True, "gross_payment_value": ":,.0f"},
    )

    show_chart(v5_apply_layout(fig, height=690))


def v5_chart_category_sunburst(df: pd.DataFrame):
    """
    Replaces the cramped sunburst with a readable category x state matrix.
    """

    category_column = get_category_column(df)

    if category_column is None or not {"customer_state", "payment_value"}.issubset(df.columns):
        st.warning("Category/state matrix skipped.")
        return

    work = df.dropna(subset=["customer_state", category_column]).copy()

    if work.empty:
        st.warning("No category/state data available.")
        return

    top_categories = work.groupby(category_column)["payment_value"].sum().sort_values(ascending=False).head(10).index
    top_states = work.groupby("customer_state")["payment_value"].sum().sort_values(ascending=False).head(10).index

    work = work[work[category_column].isin(top_categories) & work["customer_state"].isin(top_states)]

    matrix = work.pivot_table(
        index=category_column,
        columns="customer_state",
        values="payment_value",
        aggfunc="sum",
        fill_value=0,
    )

    matrix = matrix.loc[matrix.sum(axis=1).sort_values(ascending=True).index]

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=list(matrix.columns),
            y=[v5_short_label(value, 26) for value in matrix.index],
            colorscale="Blues",
            colorbar=dict(title="Gross value", tickfont=dict(color="#0B1220")),
            hovertemplate="Category: %{y}<br>State: %{x}<br>Gross value: %{z:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Category x State Revenue Matrix",
        xaxis_title="Customer State",
        yaxis_title="Product Category",
    )

    show_chart(v5_apply_layout(fig, height=640, legend=False))

def v5_chart_seller_risk_matrix(df: pd.DataFrame):
    """
    Shows seller dependency and cancellation risk.
    """

    seller_column = get_seller_column(df)

    if seller_column is None or not {"payment_value", "order_id"}.issubset(df.columns):
        st.warning("Seller matrix skipped.")
        return

    if "order_status" in df.columns:
        sellers = (
            df.dropna(subset=[seller_column])
            .groupby(seller_column)
            .agg(
                gross_payment_value=("payment_value", "sum"),
                orders=("order_id", "nunique"),
                canceled_orders=("order_status", lambda s: (s == "canceled").sum()),
            )
            .reset_index()
        )
    else:
        sellers = (
            df.dropna(subset=[seller_column])
            .groupby(seller_column)
            .agg(
                gross_payment_value=("payment_value", "sum"),
                orders=("order_id", "nunique"),
            )
            .reset_index()
        )
        sellers["canceled_orders"] = 0

    if sellers.empty:
        st.warning("No seller data available.")
        return

    sellers["orders"] = v5_safe_numeric(sellers["orders"])
    sellers["gross_payment_value"] = v5_safe_numeric(sellers["gross_payment_value"])
    sellers["aov"] = sellers["gross_payment_value"] / sellers["orders"].replace(0, pd.NA)
    sellers["aov"] = v5_safe_numeric(sellers["aov"])
    sellers["cancellation_rate"] = sellers["canceled_orders"] / sellers["orders"].replace(0, pd.NA) * 100
    sellers["cancellation_rate"] = v5_safe_numeric(sellers["cancellation_rate"])
    sellers["seller_short"] = sellers[seller_column].astype(str).str.slice(0, 12) + "..."
    sellers = sellers.sort_values("gross_payment_value", ascending=False).head(60)

    fig = px.scatter(
        sellers,
        x="orders",
        y="gross_payment_value",
        size="gross_payment_value",
        color="cancellation_rate",
        color_continuous_scale="Turbo",
        hover_name="seller_short",
        hover_data={
            "orders": ":,",
            "gross_payment_value": ":,.0f",
            "aov": ":,.1f",
            "cancellation_rate": ":.2f",
        },
        title="Seller Performance and Dependency Risk Matrix",
    )

    fig.update_layout(xaxis_title="Orders", yaxis_title="Gross Payment Value")
    show_chart(v5_apply_layout(fig, height=660))


def v5_chart_customer_frequency(df: pd.DataFrame):
    """
    Shows customer frequency as a clean ranked bar chart.
    """

    if not {"customer_unique_id", "order_id"}.issubset(df.columns):
        st.warning("Customer frequency skipped.")
        return

    customers = (
        df.groupby("customer_unique_id")["order_id"]
        .nunique()
        .rename("orders")
        .reset_index()
    )

    if customers.empty:
        st.warning("No customer frequency data available.")
        return

    def bucket(order_count: int) -> str:
        if order_count <= 1:
            return "1 order"
        if order_count == 2:
            return "2 orders"
        if order_count == 3:
            return "3 orders"
        return "4+ orders"

    customers["bucket"] = customers["orders"].map(bucket)

    summary = (
        customers.groupby("bucket")
        .agg(customers=("customer_unique_id", "nunique"))
        .reset_index()
    )

    order = ["1 order", "2 orders", "3 orders", "4+ orders"]
    summary["bucket"] = pd.Categorical(summary["bucket"], categories=order, ordered=True)
    summary = summary.sort_values("bucket")
    total_customers = summary["customers"].sum()
    summary["share"] = summary["customers"] / total_customers * 100
    summary["label"] = summary.apply(lambda row: f"{row['customers']:,.0f} customers · {row['share']:.1f}%", axis=1)

    fig = go.Figure(
        go.Bar(
            x=summary["customers"],
            y=summary["bucket"].astype(str),
            orientation="h",
            text=summary["label"],
            textposition="outside",
            textfont=dict(size=15, color="#020617"),
            marker=dict(color=["#1E3A8A", "#4F46E5", "#7C3AED", "#B45309"]),
            hovertemplate="Frequency: %{y}<br>Customers: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Customer Frequency Structure",
        xaxis_title="Customers",
        yaxis_title="Order Frequency",
    )

    show_chart(v5_apply_layout(fig, height=470, legend=False))

def v5_chart_customer_value_distribution(df: pd.DataFrame):
    """
    Shows customer value by decile to avoid unreadable long-tail distortion.
    """

    if not {"customer_unique_id", "payment_value", "order_id"}.issubset(df.columns):
        st.warning("Customer value distribution skipped.")
        return

    customers = (
        df.groupby("customer_unique_id")
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )

    if customers.empty:
        st.warning("No customer value data available.")
        return

    customers = customers.sort_values("gross_payment_value").reset_index(drop=True)
    customers["decile"] = pd.qcut(
        customers["gross_payment_value"].rank(method="first"),
        q=10,
        labels=[f"D{i}" for i in range(1, 11)],
    )

    deciles = (
        customers.groupby("decile", observed=False)
        .agg(
            gross_payment_value=("gross_payment_value", "sum"),
            customers=("customer_unique_id", "nunique"),
            median_customer_value=("gross_payment_value", "median"),
        )
        .reset_index()
    )

    deciles["label"] = deciles["gross_payment_value"].map(lambda value: format_currency(value))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=deciles["decile"].astype(str),
            y=deciles["gross_payment_value"],
            name="Gross payment value",
            marker=dict(color="#4F46E5"),
            text=deciles["label"],
            textposition="outside",
            textfont=dict(size=13, color="#020617"),
            hovertemplate="Decile: %{x}<br>Gross value: %{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=deciles["decile"].astype(str),
            y=deciles["median_customer_value"],
            name="Median customer value",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#B45309", width=4),
            marker=dict(size=8),
            hovertemplate="Decile: %{x}<br>Median customer value: %{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Customer Value Decile Ladder",
        xaxis_title="Customer Value Decile",
        yaxis_title="Gross Payment Value",
        yaxis2=dict(
            title="Median Customer Value",
            overlaying="y",
            side="right",
            showgrid=False,
            titlefont=dict(color="#0B1220", size=15),
            tickfont=dict(color="#0B1220", size=13),
        ),
    )

    show_chart(v5_apply_layout(fig, height=570))

def v5_chart_customer_state_bubble(df: pd.DataFrame):
    """
    Shows state opportunity with stronger labels and quadrant guides.
    """

    if not {"customer_state", "payment_value", "order_id", "customer_unique_id"}.issubset(df.columns):
        st.warning("Customer bubble skipped.")
        return

    states = (
        df.dropna(subset=["customer_state"])
        .groupby("customer_state")
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_unique_id", "nunique"),
        )
        .reset_index()
    )

    if states.empty:
        st.warning("No state opportunity data available.")
        return

    states["orders"] = v5_safe_numeric(states["orders"])
    states["gross_payment_value"] = v5_safe_numeric(states["gross_payment_value"])
    states["aov"] = states["gross_payment_value"] / states["orders"].replace(0, pd.NA)
    states["aov"] = v5_safe_numeric(states["aov"])

    x_mid = states["orders"].median()
    y_mid = states["aov"].median()

    fig = px.scatter(
        states,
        x="orders",
        y="aov",
        size="gross_payment_value",
        color="gross_payment_value",
        color_continuous_scale="Blues",
        hover_name="customer_state",
        text="customer_state",
        hover_data={
            "customers": ":,",
            "gross_payment_value": ":,.0f",
            "aov": ":,.1f",
        },
        title="State Opportunity Matrix",
    )

    fig.update_traces(
        textposition="top center",
        textfont=dict(size=12, color="#0B1220"),
        marker=dict(line=dict(color="#0F172A", width=0.8), opacity=0.86),
    )

    fig.add_vline(x=x_mid, line_width=2, line_dash="dot", line_color="#94A3B8")
    fig.add_hline(y=y_mid, line_width=2, line_dash="dot", line_color="#94A3B8")

    fig.update_layout(xaxis_title="Orders", yaxis_title="Average Gross Order Value")
    show_chart(v5_apply_layout(fig, height=650))

def v5_chart_category_opportunity_matrix(df: pd.DataFrame):
    """
    Shows category opportunity with readable labels and quadrant guides.
    """

    category_column = get_category_column(df)

    if category_column is None or not {"payment_value", "order_id"}.issubset(df.columns):
        st.warning("Category opportunity skipped.")
        return

    categories = (
        df.dropna(subset=[category_column])
        .groupby(category_column)
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )

    if categories.empty:
        st.warning("No category opportunity data available.")
        return

    categories["orders"] = v5_safe_numeric(categories["orders"])
    categories["gross_payment_value"] = v5_safe_numeric(categories["gross_payment_value"])
    categories["aov"] = categories["gross_payment_value"] / categories["orders"].replace(0, pd.NA)
    categories["aov"] = v5_safe_numeric(categories["aov"])
    categories["opportunity_score"] = categories["gross_payment_value"].rank(pct=True) * 0.55 + categories["aov"].rank(pct=True) * 0.45
    categories["category_short"] = categories[category_column].map(lambda value: v5_short_label(value, 22))
    categories = categories.sort_values("gross_payment_value", ascending=False).head(32)

    x_mid = categories["orders"].median()
    y_mid = categories["aov"].median()

    fig = px.scatter(
        categories,
        x="orders",
        y="aov",
        size="gross_payment_value",
        color="opportunity_score",
        color_continuous_scale="Cividis",
        hover_name="category_short",
        text="category_short",
        hover_data={
            "gross_payment_value": ":,.0f",
            "orders": ":,",
            "aov": ":,.1f",
            "opportunity_score": ":.2f",
        },
        title="Category Opportunity Matrix",
    )

    fig.update_traces(
        textposition="top center",
        textfont=dict(size=11, color="#0B1220"),
        marker=dict(line=dict(color="#0F172A", width=0.8), opacity=0.84),
    )

    fig.add_vline(x=x_mid, line_width=2, line_dash="dot", line_color="#94A3B8")
    fig.add_hline(y=y_mid, line_width=2, line_dash="dot", line_color="#94A3B8")

    fig.update_layout(xaxis_title="Orders", yaxis_title="Average Gross Order Value")
    show_chart(v5_apply_layout(fig, height=720))

def v5_chart_order_status_donut(df: pd.DataFrame):
    """
    Replaces oversized donut with ranked status share bars.
    """

    if "order_status" not in df.columns:
        st.warning("Status chart skipped.")
        return

    status = df["order_status"].value_counts().reset_index()
    status.columns = ["order_status", "orders"]

    if status.empty:
        st.warning("No status data available.")
        return

    total_orders = status["orders"].sum()
    status["share"] = status["orders"] / total_orders * 100
    status["label"] = status.apply(lambda row: f"{row['orders']:,.0f} · {row['share']:.1f}%", axis=1)
    status = status.sort_values("orders", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=status["orders"],
            y=status["order_status"],
            orientation="h",
            text=status["label"],
            textposition="outside",
            textfont=dict(size=14, color="#020617"),
            marker=dict(color="#0F766E", line=dict(color="#064E3B", width=1)),
            hovertemplate="Status: %{y}<br>Orders: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Order Status Mix",
        xaxis_title="Orders",
        yaxis_title="Order Status",
    )

    show_chart(v5_apply_layout(fig, height=520, legend=False))

def v5_chart_delivery_delay_distribution(df: pd.DataFrame):
    """
    Shows delivery delay distribution with outlier-aware zoom.
    """

    if "delivery_delay_days" not in df.columns:
        st.warning("Delivery delay skipped.")
        return

    work = df.dropna(subset=["delivery_delay_days"]).copy()

    if work.empty:
        st.warning("No delivery delay data available.")
        return

    work["delivery_delay_days"] = v5_safe_numeric(work["delivery_delay_days"])
    lower = work["delivery_delay_days"].quantile(0.01)
    upper = work["delivery_delay_days"].quantile(0.99)
    work = work[(work["delivery_delay_days"] >= lower) & (work["delivery_delay_days"] <= upper)]

    fig = px.histogram(
        work,
        x="delivery_delay_days",
        nbins=70,
        title="Delivery Delay Distribution · P1–P99 Zoom",
        labels={"delivery_delay_days": "Delivery Delay Days"},
        color_discrete_sequence=["#B45309"],
    )

    fig.add_vline(x=0, line_width=3, line_dash="dash", line_color="#0F766E")
    fig.update_layout(yaxis_title="Orders")
    show_chart(v5_apply_layout(fig, height=540, legend=False))

def v5_chart_late_delivery_heatmap(df: pd.DataFrame):
    """
    Shows late-delivery pressure by state and category.
    """

    category_column = get_category_column(df)

    if category_column is None or not {"customer_state", "is_late_delivery"}.issubset(df.columns):
        st.warning("Late delivery heatmap skipped.")
        return

    work = df.dropna(subset=["customer_state", category_column]).copy()

    if work.empty:
        st.warning("No late delivery data available.")
        return

    work["is_late_delivery"] = v5_safe_numeric(work["is_late_delivery"])

    top_states = work.groupby("customer_state")["is_late_delivery"].count().sort_values(ascending=False).head(12).index
    top_categories = work.groupby(category_column)["is_late_delivery"].count().sort_values(ascending=False).head(10).index

    work = work[work["customer_state"].isin(top_states) & work[category_column].isin(top_categories)]

    pivot = work.pivot_table(
        index="customer_state",
        columns=category_column,
        values="is_late_delivery",
        aggfunc="mean",
        fill_value=0,
    ) * 100

    if pivot.empty:
        st.warning("No late delivery heatmap data available.")
        return

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[v5_short_label(x, 24) for x in pivot.columns],
            y=list(pivot.index),
            colorscale="Reds",
            colorbar=dict(title="Late %"),
            hovertemplate="State: %{y}<br>Category: %{x}<br>Late delivery: %{z:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(title="Late Delivery Pressure Heatmap", xaxis_title="Product Category", yaxis_title="Customer State")
    fig = v5_apply_layout(fig, height=640, legend=False)
    fig.update_xaxes(tickangle=-35)
    show_chart(fig)


def v5_chart_payment_intelligence(df: pd.DataFrame):
    """
    Shows payment method value as readable horizontal bars.
    """

    payment_column = get_payment_column(df)

    if payment_column is None or not {"payment_value", "order_id"}.issubset(df.columns):
        st.warning("Payment mix skipped.")
        return

    payment = (
        df.dropna(subset=[payment_column])
        .groupby(payment_column)
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("gross_payment_value", ascending=True)
        .reset_index()
    )

    if payment.empty:
        st.warning("No payment data available.")
        return

    payment["aov"] = payment["gross_payment_value"] / payment["orders"].replace(0, pd.NA)
    payment["aov"] = v5_safe_numeric(payment["aov"])
    payment["label"] = payment.apply(
        lambda row: f"{format_currency(row['gross_payment_value'])} · AOV {format_currency(row['aov'])}",
        axis=1,
    )

    fig = go.Figure(
        go.Bar(
            x=payment["gross_payment_value"],
            y=payment[payment_column].astype(str),
            orientation="h",
            text=payment["label"],
            textposition="outside",
            textfont=dict(size=14, color="#020617"),
            marker=dict(color="#2563EB", line=dict(color="#1E3A8A", width=1)),
            hovertemplate="Payment: %{y}<br>Gross value: %{x:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Payment Method Revenue and AOV",
        xaxis_title="Gross Payment Value",
        yaxis_title="Payment Type",
    )

    show_chart(v5_apply_layout(fig, height=520, legend=False))

def v5_chart_installment_profile(df: pd.DataFrame):
    """
    Shows installment behavior with clearer dual-axis contrast.
    """

    if not {"payment_installments", "payment_value", "order_id"}.issubset(df.columns):
        st.warning("Installment profile skipped.")
        return

    work = df.dropna(subset=["payment_installments"]).copy()

    if work.empty:
        st.warning("No installment data available.")
        return

    work["payment_installments"] = v5_safe_numeric(work["payment_installments"]).astype(int)

    installments = (
        work.groupby("payment_installments")
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
        .sort_values("payment_installments")
    )

    installments = installments[installments["payment_installments"] <= 12]

    if installments.empty:
        st.warning("No installment profile data available.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=installments["payment_installments"].astype(str),
            y=installments["gross_payment_value"],
            name="Gross payment value",
            marker=dict(color="#4F46E5", line=dict(color="#312E81", width=1)),
            hovertemplate="Installments: %{x}<br>Gross value: %{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=installments["payment_installments"].astype(str),
            y=installments["orders"],
            name="Orders",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#92400E", width=5),
            marker=dict(size=9, color="#92400E"),
            hovertemplate="Installments: %{x}<br>Orders: %{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Installment Profile: Revenue and Orders",
        xaxis_title="Payment Installments",
        yaxis_title="Gross Payment Value",
        yaxis2=dict(
            title="Orders",
            overlaying="y",
            side="right",
            showgrid=False,
            titlefont=dict(color="#0B1220", size=15),
            tickfont=dict(color="#0B1220", size=13),
        ),
    )

    show_chart(v5_apply_layout(fig, height=590))

def v5_chart_3d_revenue_lab(df: pd.DataFrame):
    """
    Shows 3D revenue by month, category, and gross value with stronger contrast.
    """

    category_column = get_category_column(df)

    if category_column is None or not {"order_purchase_timestamp", "payment_value", "order_id"}.issubset(df.columns):
        st.warning("3D revenue lab skipped.")
        return

    work = df.dropna(subset=["order_purchase_timestamp", category_column, "payment_value"]).copy()

    if work.empty:
        st.warning("No 3D revenue data available.")
        return

    top_categories = work.groupby(category_column)["payment_value"].sum().sort_values(ascending=False).head(10).index
    work = work[work[category_column].isin(top_categories)].copy()
    work["order_month"] = work["order_purchase_timestamp"].dt.to_period("M").astype(str)

    agg = (
        work.groupby(["order_month", category_column])
        .agg(
            gross_payment_value=("payment_value", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )

    if agg.empty:
        st.warning("No 3D revenue aggregation available.")
        return

    agg["month_index"] = pd.factorize(agg["order_month"])[0]
    agg["category_index"] = pd.factorize(agg[category_column])[0]
    agg["bubble_size"] = agg["orders"].rank(pct=True).fillna(0) * 20 + 7

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=agg["month_index"],
                y=agg["category_index"],
                z=agg["gross_payment_value"],
                mode="markers",
                marker=dict(
                    size=agg["bubble_size"],
                    color=agg["gross_payment_value"],
                    colorscale="Turbo",
                    opacity=0.92,
                    line=dict(color="#0B1220", width=0.8),
                    colorbar=dict(title="Gross value", tickfont=dict(color="#0B1220")),
                ),
                text=(
                    "Month: " + agg["order_month"].astype(str)
                    + "<br>Category: " + agg[category_column].astype(str)
                    + "<br>Gross value: " + agg["gross_payment_value"].round(0).astype(str)
                    + "<br>Orders: " + agg["orders"].astype(str)
                ),
                hovertemplate="%{text}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="3D Revenue Landscape", font=dict(size=27, color="#020617", family="Arial Black")),
        height=820,
        margin=dict(l=10, r=10, t=90, b=10),
        scene=dict(
            xaxis=dict(title="Month index", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1", color="#0B1220"),
            yaxis=dict(title="Category index", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1", color="#0B1220"),
            zaxis=dict(title="Gross Payment Value", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1", color="#0B1220"),
            camera=dict(eye=dict(x=1.65, y=1.75, z=1.15)),
        ),
        paper_bgcolor="#FFFFFF",
        font=dict(color="#0B1220", size=14),
    )

    show_chart(fig)

def v5_chart_3d_seller_lab(df: pd.DataFrame):
    """
    Shows 3D seller risk by orders, cancellation rate, and gross value.
    """

    seller_column = get_seller_column(df)

    if seller_column is None or not {"payment_value", "order_id"}.issubset(df.columns):
        st.warning("3D seller lab skipped.")
        return

    if "order_status" in df.columns:
        sellers = (
            df.dropna(subset=[seller_column])
            .groupby(seller_column)
            .agg(
                gross_payment_value=("payment_value", "sum"),
                orders=("order_id", "nunique"),
                canceled_orders=("order_status", lambda s: (s == "canceled").sum()),
            )
            .reset_index()
        )
    else:
        sellers = (
            df.dropna(subset=[seller_column])
            .groupby(seller_column)
            .agg(
                gross_payment_value=("payment_value", "sum"),
                orders=("order_id", "nunique"),
            )
            .reset_index()
        )
        sellers["canceled_orders"] = 0

    if sellers.empty:
        st.warning("No 3D seller data available.")
        return

    sellers["orders"] = v5_safe_numeric(sellers["orders"])
    sellers["gross_payment_value"] = v5_safe_numeric(sellers["gross_payment_value"])
    sellers["cancellation_rate"] = sellers["canceled_orders"] / sellers["orders"].replace(0, pd.NA) * 100
    sellers["cancellation_rate"] = v5_safe_numeric(sellers["cancellation_rate"])
    sellers["seller_short"] = sellers[seller_column].astype(str).str.slice(0, 12) + "..."
    sellers = sellers.sort_values("gross_payment_value", ascending=False).head(80)
    sellers["bubble_size"] = sellers["gross_payment_value"].rank(pct=True).fillna(0) * 18 + 7

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=sellers["orders"],
                y=sellers["cancellation_rate"],
                z=sellers["gross_payment_value"],
                mode="markers",
                marker=dict(
                    size=sellers["bubble_size"],
                    color=sellers["gross_payment_value"],
                    colorscale="Viridis",
                    opacity=0.92,
                    line=dict(color="#0B1220", width=0.8),
                    colorbar=dict(title="Gross value", tickfont=dict(color="#0B1220")),
                ),
                text=(
                    "Seller: " + sellers["seller_short"].astype(str)
                    + "<br>Orders: " + sellers["orders"].astype(int).astype(str)
                    + "<br>Cancellation rate: " + sellers["cancellation_rate"].round(2).astype(str) + "%"
                    + "<br>Gross value: " + sellers["gross_payment_value"].round(0).astype(str)
                ),
                hovertemplate="%{text}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="3D Seller Risk Cube", font=dict(size=27, color="#020617", family="Arial Black")),
        height=820,
        margin=dict(l=10, r=10, t=90, b=10),
        scene=dict(
            xaxis=dict(title="Orders", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1", color="#0B1220"),
            yaxis=dict(title="Cancellation Rate", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1", color="#0B1220"),
            zaxis=dict(title="Gross Payment Value", backgroundcolor="#F8FAFC", gridcolor="#CBD5E1", color="#0B1220"),
            camera=dict(eye=dict(x=1.65, y=1.65, z=1.12)),
        ),
        paper_bgcolor="#FFFFFF",
        font=dict(color="#0B1220", size=14),
    )

    show_chart(fig)

def v5_data_quality_control_room(df: pd.DataFrame):
    """
    Shows data quality indicators and a missingness heatmap.
    """

    v5_section_brief(
        "Data quality control room",
        "This page checks row volume, duplicate order IDs, missing payment values, and column coverage before business interpretation.",
    )

    show_data_quality(df)

    key_columns = [
        "order_id",
        "customer_unique_id",
        "order_status",
        "payment_value",
        "customer_state",
        "order_purchase_timestamp",
        get_category_column(df),
        get_payment_column(df),
        get_seller_column(df),
        "delivery_delay_days",
        "is_late_delivery",
        "review_score",
    ]

    key_columns = [column for column in key_columns if column and column in df.columns]

    if key_columns:
        missing = df[key_columns].isna().mean().mul(100).reset_index()
        missing.columns = ["column", "missing_percent"]

        fig = go.Figure(
            data=go.Heatmap(
                z=[missing["missing_percent"].tolist()],
                x=missing["column"].tolist(),
                y=["Missingness"],
                colorscale="Reds",
                colorbar=dict(title="Missing %"),
                hovertemplate="Column: %{x}<br>Missing: %{z:.2f}%<extra></extra>",
            )
        )

        fig.update_layout(title="Critical Column Missingness Heatmap", xaxis_title="Column", yaxis_title="")
        fig = v5_apply_layout(fig, height=370, legend=False)
        fig.update_xaxes(tickangle=-35)
        show_chart(fig)

    with st.expander("Preview filtered dataset"):
        st.dataframe(df.head(200), use_container_width=True)

    with st.expander("Available columns"):
        st.write(list(df.columns))



# V5_DARK_NO_WATERFALL_THEME_START

st.markdown(
    """
    <style>
        :root {
            --bg0: #020617;
            --bg1: #07111F;
            --bg2: #0F172A;
            --panel: #111827;
            --panel2: #0B1220;
            --border: #334155;
            --text: #F8FAFC;
            --muted: #CBD5E1;
            --muted2: #94A3B8;
            --accent: #8B5CF6;
            --accent2: #14B8A6;
            --warn: #F59E0B;
            --risk: #F43F5E;
        }

        html, body, [class*="css"], .stApp {
            background:
                radial-gradient(circle at top left, rgba(139,92,246,0.20), transparent 34rem),
                radial-gradient(circle at top right, rgba(20,184,166,0.15), transparent 32rem),
                linear-gradient(180deg, #020617 0%, #07111F 48%, #020617 100%) !important;
            color: var(--text) !important;
        }

        .block-container {
            max-width: 1580px !important;
            padding-top: 1.1rem !important;
            padding-bottom: 3rem !important;
        }

        .main-header {
            background:
                radial-gradient(circle at top right, rgba(244,63,94,0.32), transparent 26rem),
                linear-gradient(135deg, #020617 0%, #1E1B4B 52%, #3B0764 100%) !important;
            border: 1px solid rgba(148,163,184,0.35) !important;
            border-radius: 32px !important;
            box-shadow: 0 34px 90px rgba(0,0,0,0.55) !important;
        }

        .main-title {
            color: #FFFFFF !important;
            text-shadow: 0 2px 18px rgba(139,92,246,0.35) !important;
        }

        .main-subtitle {
            color: #E2E8F0 !important;
            font-weight: 650 !important;
        }

        .main-header::after {
            background: rgba(15,23,42,0.72) !important;
            border: 1px solid rgba(148,163,184,0.45) !important;
            color: #FFFFFF !important;
        }

        .section-title {
            color: #F8FAFC !important;
            font-size: 1.6rem !important;
            font-weight: 950 !important;
        }

        .section-brief, .grain-card {
            background: linear-gradient(135deg, rgba(17,24,39,0.96), rgba(15,23,42,0.92)) !important;
            color: #E2E8F0 !important;
            border: 1px solid rgba(148,163,184,0.28) !important;
            border-left: 7px solid #8B5CF6 !important;
            box-shadow: 0 22px 55px rgba(0,0,0,0.42) !important;
        }

        .section-brief-title {
            color: #FFFFFF !important;
            font-weight: 950 !important;
        }

        .section-brief-text {
            color: #CBD5E1 !important;
            font-weight: 650 !important;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(17,24,39,0.98), rgba(11,18,32,0.96)) !important;
            border: 1px solid rgba(148,163,184,0.25) !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.45) !important;
        }

        .metric-label {
            color: #CBD5E1 !important;
            font-weight: 950 !important;
        }

        .metric-value {
            color: #FFFFFF !important;
            font-weight: 950 !important;
            text-shadow: 0 2px 18px rgba(139,92,246,0.25) !important;
        }

        .metric-note {
            color: #CBD5E1 !important;
            font-weight: 650 !important;
        }

        .metric-badge {
            border-width: 1px !important;
            font-weight: 950 !important;
        }

        .badge-good {
            background: rgba(20,184,166,0.18) !important;
            color: #5EEAD4 !important;
            border-color: rgba(94,234,212,0.42) !important;
        }

        .badge-watch {
            background: rgba(245,158,11,0.18) !important;
            color: #FCD34D !important;
            border-color: rgba(252,211,77,0.42) !important;
        }

        .badge-risk {
            background: rgba(244,63,94,0.18) !important;
            color: #FDA4AF !important;
            border-color: rgba(253,164,175,0.42) !important;
        }

        .badge-info {
            background: rgba(139,92,246,0.20) !important;
            color: #DDD6FE !important;
            border-color: rgba(196,181,253,0.42) !important;
        }

        div[data-testid="stPlotlyChart"] {
            background: linear-gradient(180deg, rgba(17,24,39,0.98), rgba(11,18,32,0.98)) !important;
            border: 1px solid rgba(148,163,184,0.26) !important;
            border-radius: 28px !important;
            box-shadow: 0 26px 70px rgba(0,0,0,0.48) !important;
            padding: 1.25rem !important;
            margin-bottom: 1.5rem !important;
        }

        div[role="radiogroup"] {
            background: rgba(15,23,42,0.92) !important;
            border: 1px solid rgba(148,163,184,0.28) !important;
            border-radius: 999px !important;
            box-shadow: 0 18px 42px rgba(0,0,0,0.35) !important;
        }

        div[role="radiogroup"] label p {
            color: #E2E8F0 !important;
            font-weight: 850 !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617 0%, #0F172A 100%) !important;
            border-right: 1px solid rgba(148,163,184,0.24) !important;
        }

        section[data-testid="stSidebar"] * {
            color: #E2E8F0 !important;
            font-weight: 650 !important;
        }

        section[data-testid="stSidebar"] .sidebar-brand {
            background: linear-gradient(135deg, #1E1B4B, #312E81, #581C87) !important;
            border: 1px solid rgba(196,181,253,0.30) !important;
            box-shadow: 0 20px 46px rgba(0,0,0,0.48) !important;
        }

        section[data-testid="stSidebar"] .sidebar-brand,
        section[data-testid="stSidebar"] .sidebar-brand * {
            color: #FFFFFF !important;
        }

        div[data-testid="stMetric"],
        div[data-testid="stDateInput"],
        div[data-baseweb="select"] {
            background: rgba(15,23,42,0.65) !important;
            color: #F8FAFC !important;
        }

        input, textarea, select {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            border-color: #334155 !important;
        }

        hr {
            border-color: rgba(148,163,184,0.22) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# V5_DARK_NO_WATERFALL_THEME_END


# V5_APPLE_PRO_DARK_POLISH_START

st.markdown(
    """
    <style>
        :root {
            --apple-bg-0: #020617;
            --apple-bg-1: #050816;
            --apple-bg-2: #0B1020;
            --apple-panel: rgba(15, 23, 42, 0.72);
            --apple-panel-solid: #0F172A;
            --apple-card: rgba(17, 24, 39, 0.76);
            --apple-border: rgba(148, 163, 184, 0.22);
            --apple-border-strong: rgba(203, 213, 225, 0.34);
            --apple-text: #F8FAFC;
            --apple-muted: #CBD5E1;
            --apple-muted-2: #94A3B8;
            --apple-purple: #A78BFA;
            --apple-blue: #60A5FA;
            --apple-teal: #5EEAD4;
            --apple-pink: #F9A8D4;
            --apple-amber: #FCD34D;
            --apple-red: #FDA4AF;
        }

        html,
        body,
        [class*="css"],
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", sans-serif !important;
            color: var(--apple-text) !important;
            background:
                radial-gradient(circle at 12% 0%, rgba(96, 165, 250, 0.18), transparent 33rem),
                radial-gradient(circle at 88% 4%, rgba(167, 139, 250, 0.18), transparent 36rem),
                radial-gradient(circle at 50% 95%, rgba(20, 184, 166, 0.08), transparent 40rem),
                linear-gradient(180deg, #020617 0%, #050816 44%, #020617 100%) !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0rem !important;
        }

        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"] {
            display: none !important;
        }

        div[data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 20% 0%, rgba(96,165,250,0.12), transparent 34rem),
                radial-gradient(circle at 82% 4%, rgba(167,139,250,0.16), transparent 38rem),
                linear-gradient(180deg, #020617 0%, #050816 48%, #020617 100%) !important;
        }

        div[data-testid="stSidebar"] {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(2,6,23,0.98), rgba(15,23,42,0.94)) !important;
            border-right: 1px solid rgba(148,163,184,0.18) !important;
            box-shadow: 18px 0 55px rgba(0,0,0,0.35) !important;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 2.15rem !important;
        }

        .block-container {
            max-width: 1600px !important;
            padding-top: 0.65rem !important;
            padding-bottom: 3.4rem !important;
            padding-left: 4.7rem !important;
            padding-right: 4.7rem !important;
        }

        .main-header {
            margin-top: 0.15rem !important;
            margin-bottom: 1.75rem !important;
            padding: 2.25rem 2.55rem !important;
            border-radius: 34px !important;
            background:
                radial-gradient(circle at 88% 10%, rgba(236,72,153,0.26), transparent 26rem),
                radial-gradient(circle at 18% 10%, rgba(96,165,250,0.18), transparent 24rem),
                linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,27,75,0.94) 52%, rgba(88,28,135,0.92) 100%) !important;
            border: 1px solid rgba(203,213,225,0.26) !important;
            box-shadow:
                0 38px 110px rgba(0,0,0,0.55),
                inset 0 1px 0 rgba(255,255,255,0.08) !important;
            backdrop-filter: blur(22px) saturate(155%) !important;
            -webkit-backdrop-filter: blur(22px) saturate(155%) !important;
        }

        .main-title {
            color: #FFFFFF !important;
            font-size: 3.12rem !important;
            line-height: 1.02 !important;
            font-weight: 850 !important;
            letter-spacing: -0.065em !important;
            text-shadow: 0 0 34px rgba(167,139,250,0.32) !important;
        }

        .main-subtitle {
            color: #DDE6F3 !important;
            font-size: 1.08rem !important;
            line-height: 1.65 !important;
            font-weight: 620 !important;
            max-width: 1120px !important;
        }

        .main-header::after {
            background: rgba(2, 6, 23, 0.46) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(226,232,240,0.28) !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.10),
                0 12px 30px rgba(0,0,0,0.20) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
        }

        .sidebar-brand {
            border-radius: 26px !important;
            padding: 1.25rem 1.18rem !important;
            margin-bottom: 1.45rem !important;
            background:
                radial-gradient(circle at top right, rgba(167,139,250,0.30), transparent 11rem),
                linear-gradient(135deg, rgba(15,23,42,0.96), rgba(49,46,129,0.88), rgba(88,28,135,0.82)) !important;
            border: 1px solid rgba(196,181,253,0.30) !important;
            box-shadow:
                0 24px 60px rgba(0,0,0,0.48),
                inset 0 1px 0 rgba(255,255,255,0.08) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
        }

        .sidebar-brand-title {
            color: #FFFFFF !important;
            font-size: 1.12rem !important;
            font-weight: 820 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.22 !important;
        }

        .sidebar-brand-subtitle {
            color: #EDE9FE !important;
            font-size: 0.88rem !important;
            line-height: 1.55 !important;
            font-weight: 650 !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            letter-spacing: -0.025em !important;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #DDE6F3 !important;
            font-weight: 650 !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(148,163,184,0.18) !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"],
        input {
            background: rgba(15,23,42,0.88) !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(148,163,184,0.30) !important;
            border-radius: 15px !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 10px 28px rgba(0,0,0,0.18) !important;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="input"] > div:hover,
        input:focus {
            border-color: rgba(167,139,250,0.72) !important;
            box-shadow:
                0 0 0 3px rgba(167,139,250,0.13),
                inset 0 1px 0 rgba(255,255,255,0.06) !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] svg,
        div[data-baseweb="input"] input,
        input::placeholder {
            color: #F1F5F9 !important;
            fill: #F1F5F9 !important;
        }

        ul[role="listbox"],
        div[data-baseweb="popover"] {
            background: #0B1220 !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(148,163,184,0.26) !important;
            border-radius: 16px !important;
        }

        li[role="option"] {
            background: #0B1220 !important;
            color: #F8FAFC !important;
        }

        li[role="option"]:hover {
            background: rgba(167,139,250,0.18) !important;
        }

        div[data-testid="stMetric"] {
            background:
                linear-gradient(180deg, rgba(17,24,39,0.82), rgba(8,13,26,0.86)) !important;
            border: 1px solid rgba(148,163,184,0.28) !important;
            border-radius: 24px !important;
            padding: 1.0rem 1.1rem !important;
            box-shadow:
                0 20px 48px rgba(0,0,0,0.34),
                inset 0 1px 0 rgba(255,255,255,0.05) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #CBD5E1 !important;
            font-weight: 760 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-weight: 820 !important;
        }

        .section-title {
            color: #FFFFFF !important;
            font-size: 1.62rem !important;
            font-weight: 820 !important;
            letter-spacing: -0.045em !important;
            margin-top: 0.55rem !important;
            margin-bottom: 1rem !important;
        }

        .metric-card {
            position: relative !important;
            overflow: hidden !important;
            border-radius: 26px !important;
            min-height: 156px !important;
            background:
                radial-gradient(circle at 88% 0%, rgba(167,139,250,0.12), transparent 10rem),
                linear-gradient(180deg, rgba(17,24,39,0.86), rgba(8,13,26,0.92)) !important;
            border: 1px solid rgba(148,163,184,0.26) !important;
            box-shadow:
                0 24px 60px rgba(0,0,0,0.42),
                inset 0 1px 0 rgba(255,255,255,0.055) !important;
            backdrop-filter: blur(18px) saturate(150%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(150%) !important;
        }

        .metric-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 5px;
            background: linear-gradient(180deg, #A78BFA, #60A5FA, #5EEAD4);
            opacity: 0.95;
        }

        .metric-card::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, rgba(255,255,255,0.06), transparent 42%);
            pointer-events: none;
        }

        .metric-label {
            color: #CBD5E1 !important;
            font-size: 0.80rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.075em !important;
        }

        .metric-value {
            color: #FFFFFF !important;
            font-size: 2.24rem !important;
            font-weight: 820 !important;
            letter-spacing: -0.055em !important;
            text-shadow: 0 0 30px rgba(96,165,250,0.20) !important;
        }

        .metric-note {
            color: #D7DEE9 !important;
            font-size: 0.91rem !important;
            line-height: 1.5 !important;
            font-weight: 650 !important;
        }

        .metric-badge {
            border-radius: 999px !important;
            font-size: 0.69rem !important;
            font-weight: 820 !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.12) !important;
        }

        .badge-good {
            background: rgba(20,184,166,0.16) !important;
            color: #99F6E4 !important;
            border-color: rgba(94,234,212,0.38) !important;
        }

        .badge-watch {
            background: rgba(245,158,11,0.16) !important;
            color: #FDE68A !important;
            border-color: rgba(252,211,77,0.38) !important;
        }

        .badge-risk {
            background: rgba(244,63,94,0.17) !important;
            color: #FECDD3 !important;
            border-color: rgba(253,164,175,0.38) !important;
        }

        .badge-info {
            background: rgba(139,92,246,0.18) !important;
            color: #EDE9FE !important;
            border-color: rgba(196,181,253,0.38) !important;
        }

        .grain-card,
        .section-brief {
            border-radius: 26px !important;
            background:
                radial-gradient(circle at top left, rgba(96,165,250,0.10), transparent 19rem),
                linear-gradient(180deg, rgba(17,24,39,0.82), rgba(8,13,26,0.90)) !important;
            border: 1px solid rgba(148,163,184,0.25) !important;
            border-left: 7px solid #A78BFA !important;
            color: #E5E7EB !important;
            font-size: 1rem !important;
            font-weight: 630 !important;
            box-shadow:
                0 24px 62px rgba(0,0,0,0.42),
                inset 0 1px 0 rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(18px) saturate(140%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(140%) !important;
        }

        .section-brief-title {
            color: #FFFFFF !important;
            font-size: 1.1rem !important;
            font-weight: 820 !important;
            letter-spacing: -0.025em !important;
        }

        .section-brief-text {
            color: #D7DEE9 !important;
            font-size: 0.99rem !important;
            line-height: 1.62 !important;
            font-weight: 650 !important;
        }

        div[role="radiogroup"] {
            padding: 0.50rem !important;
            border-radius: 999px !important;
            background:
                linear-gradient(180deg, rgba(17,24,39,0.78), rgba(8,13,26,0.90)) !important;
            border: 1px solid rgba(148,163,184,0.30) !important;
            box-shadow:
                0 22px 52px rgba(0,0,0,0.40),
                inset 0 1px 0 rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(18px) saturate(140%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(140%) !important;
        }

        div[role="radiogroup"] label {
            padding: 0.34rem 0.50rem !important;
            border-radius: 999px !important;
            transition: background 160ms ease, transform 160ms ease !important;
        }

        div[role="radiogroup"] label:hover {
            background: rgba(167,139,250,0.14) !important;
            transform: translateY(-1px);
        }

        div[role="radiogroup"] label p {
            color: #E5E7EB !important;
            font-weight: 780 !important;
            font-size: 0.95rem !important;
            letter-spacing: -0.015em !important;
        }

        div[data-testid="stPlotlyChart"] {
            background:
                radial-gradient(circle at top left, rgba(96,165,250,0.06), transparent 20rem),
                linear-gradient(180deg, rgba(17,24,39,0.90), rgba(8,13,26,0.95)) !important;
            border: 1px solid rgba(148,163,184,0.24) !important;
            border-radius: 30px !important;
            padding: 1.35rem !important;
            margin-bottom: 1.65rem !important;
            box-shadow:
                0 28px 72px rgba(0,0,0,0.45),
                inset 0 1px 0 rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(16px) saturate(135%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(135%) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stHorizontalBlock"],
        div[data-testid="column"] {
            background: transparent !important;
        }

        hr {
            border-color: rgba(148,163,184,0.18) !important;
        }

        ::selection {
            background: rgba(167,139,250,0.36) !important;
            color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# V5_APPLE_PRO_DARK_POLISH_END

# MINIMAL_HEADER_AND_EXPLANATION_CSS_START

st.markdown(
    """
    <style>
        .main-header {
            position: relative !important;
            overflow: hidden !important;
            padding: 2.3rem 2.5rem !important;
            margin: 0.35rem 0 1.8rem 0 !important;
            border-radius: 30px !important;
            background:
                radial-gradient(circle at 82% 28%, rgba(88,80,236,0.34), transparent 22rem),
                radial-gradient(circle at 96% 72%, rgba(192,38,211,0.22), transparent 18rem),
                radial-gradient(circle at 12% 12%, rgba(14,165,233,0.13), transparent 22rem),
                linear-gradient(135deg, #061225 0%, #0B1230 52%, #1E1044 100%) !important;
            border: 1px solid rgba(126,146,255,0.30) !important;
            box-shadow: 0 30px 90px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.08) !important;
        }

        .hero-eyebrow {
            display: inline-flex !important;
            width: fit-content !important;
            padding: 0.52rem 0.92rem !important;
            margin-bottom: 1.05rem !important;
            border-radius: 999px !important;
            background: rgba(38,72,166,0.26) !important;
            border: 1px solid rgba(96,165,250,0.38) !important;
            color: #7EA2FF !important;
            font-size: 0.76rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.22em !important;
        }

        .main-title {
            color: #FFFFFF !important;
            font-size: clamp(2.8rem, 4vw, 4.4rem) !important;
            line-height: 0.98 !important;
            font-weight: 900 !important;
            letter-spacing: -0.07em !important;
            margin: 0 0 1rem 0 !important;
        }

        .main-subtitle {
            max-width: 900px !important;
            color: #DDE7F8 !important;
            font-size: 1.08rem !important;
            line-height: 1.72 !important;
            font-weight: 600 !important;
        }

        .sidebar-brand {
            padding: 1.15rem !important;
            border-radius: 24px !important;
            background:
                radial-gradient(circle at 100% 0%, rgba(168,85,247,0.30), transparent 9rem),
                linear-gradient(135deg, rgba(30,54,118,0.96), rgba(83,45,155,0.96)) !important;
            border: 1px solid rgba(153,126,255,0.34) !important;
            box-shadow: 0 18px 48px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.08) !important;
            margin-bottom: 1.4rem !important;
        }

        .sidebar-brand-title {
            color: #FFFFFF !important;
            font-size: 1.16rem !important;
            line-height: 1.16 !important;
            font-weight: 900 !important;
            letter-spacing: -0.04em !important;
            margin-bottom: 0.7rem !important;
        }

        .sidebar-brand-subtitle {
            color: #E8EEFF !important;
            font-size: 0.9rem !important;
            line-height: 1.6 !important;
            font-weight: 600 !important;
        }

        .chart-story-card {
            margin: 0.25rem 0 1.4rem 0 !important;
            padding: 1rem 1.1rem !important;
            border-radius: 18px !important;
            background: linear-gradient(180deg, rgba(10,20,40,0.96), rgba(5,12,26,0.96)) !important;
            border: 1px solid rgba(126,146,255,0.20) !important;
            border-left: 5px solid #8B5CF6 !important;
            box-shadow: 0 14px 34px rgba(0,0,0,0.24) !important;
        }

        .chart-story-title {
            color: #FFFFFF !important;
            font-size: 1.04rem !important;
            font-weight: 900 !important;
            margin-bottom: 0.55rem !important;
        }

        .chart-story-body {
            color: #DDE7F8 !important;
            font-size: 0.94rem !important;
            line-height: 1.78 !important;
            font-weight: 600 !important;
        }

        .chart-story-body b {
            color: #FFFFFF !important;
            font-weight: 900 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# MINIMAL_HEADER_AND_EXPLANATION_CSS_END

# MINIMAL_CHART_EXPLANATION_WRAPPER_START

def _minimal_chart_story_from_title(title: str) -> dict[str, str]:
    """
    Return a simple business explanation for a chart.

    The function is intentionally title-based because it must not modify chart
    data, chart rendering, tabs, filters, or KPI calculations. It keeps the
    explanation easy to understand for portfolio reviewers and non-technical
    users.
    """
    import re as _re

    clean_title = _re.sub(r"<.*?>", " ", str(title or ""))
    clean_title = _re.sub(r"[_\-]+", " ", clean_title)
    clean_title = _re.sub(r"\s+", " ", clean_title).strip().lower()

    def has_any(*words: str) -> bool:
        return any(word in clean_title for word in words)

    if has_any("3d", "scatter", "cube", "landscape"):
        return {
            "question": "Which groups stand out when several business signals are compared together?",
            "read": "Look for points that sit far away from the main group. These are the outliers worth checking first.",
            "conclusion": "The chart helps spot unusual revenue, customer, seller, or delivery patterns that flat charts may hide.",
            "action": "Review the outlier groups and decide whether they are high-value opportunities or operational risks.",
        }

    if has_any("revenue", "payment value", "gross", "delivered revenue", "sales", "value"):
        return {
            "question": "How much business value is being created, and how much of it is actually delivered?",
            "read": "Higher values show stronger business performance. Gaps or drops show where revenue may be leaking.",
            "conclusion": "The strongest result is where demand turns into delivered revenue without a large gap.",
            "action": "Focus on the periods, categories, or segments where revenue is high but delivery or leakage needs attention.",
        }

    if has_any("leakage", "cancel", "cancelled", "canceled", "unavailable"):
        return {
            "question": "Where is business value being lost before it becomes completed revenue?",
            "read": "Higher leakage, cancellations, or unavailable orders mean more value is being lost.",
            "conclusion": "These areas reduce revenue quality and should be treated as business loss, not just operations noise.",
            "action": "Investigate the biggest leakage sources and fix the process, seller, or fulfillment issue behind them.",
        }

    if has_any("delivery", "late", "delay", "freight", "fulfillment", "status"):
        return {
            "question": "How reliable is the order delivery process?",
            "read": "Look for late delivery, weak status performance, or delivery patterns that move in the wrong direction.",
            "conclusion": "Poor delivery performance can reduce customer trust and weaken future sales.",
            "action": "Prioritize the regions, sellers, or time periods where delivery risk is highest.",
        }

    if has_any("customer", "repeat", "retention", "audience", "cohort"):
        return {
            "question": "What does this chart say about customer behavior?",
            "read": "Look at where customers are concentrated, how often they return, and which groups create more value.",
            "conclusion": "Customer performance is stronger when more customers return and value is not dependent on only one group.",
            "action": "Use the strongest customer groups for retention campaigns and investigate weak repeat behavior.",
        }

    if has_any("seller", "merchant", "vendor"):
        return {
            "question": "Which sellers are helping or hurting business performance?",
            "read": "Compare sellers by value, order volume, review quality, and operational risk.",
            "conclusion": "A seller is valuable only when high revenue comes with reliable fulfillment and good customer outcomes.",
            "action": "Support strong sellers and review sellers with high value but weak delivery, cancellation, or review signals.",
        }

    if has_any("product", "category", "items", "catalog", "sku"):
        return {
            "question": "Which products or categories are driving performance?",
            "read": "Bigger values show stronger product contribution. Weak quality or delivery signals show product risk.",
            "conclusion": "The best categories combine strong revenue, reliable delivery, and healthy customer response.",
            "action": "Prioritize top-performing categories and investigate categories with high value but weak quality signals.",
        }

    if has_any("payment", "installment", "card", "wallet", "voucher"):
        return {
            "question": "How do customers prefer to pay?",
            "read": "Compare payment methods or installment patterns by order volume and value.",
            "conclusion": "Payment behavior shows checkout preference and affordability patterns.",
            "action": "Make the strongest payment methods easy to use and watch payment types linked to weaker conversion or risk.",
        }

    if has_any("review", "score", "rating", "satisfaction"):
        return {
            "question": "How satisfied are customers with the buying experience?",
            "read": "Higher review scores mean better customer experience. Drops or weak groups need attention.",
            "conclusion": "Customer satisfaction is a quality signal that can affect repeat purchase and brand trust.",
            "action": "Find the categories, sellers, or regions with low scores and fix the root cause.",
        }

    if has_any("state", "city", "region", "geo", "map", "location"):
        return {
            "question": "Where is performance strongest or weakest by location?",
            "read": "Compare regions by value, orders, customers, and operational quality.",
            "conclusion": "Regional differences show where the business can grow and where service quality needs control.",
            "action": "Invest in strong regions and investigate regions with high demand but weak delivery or satisfaction.",
        }

    if has_any("data", "missing", "quality", "null", "completeness"):
        return {
            "question": "Can this data be trusted for business decisions?",
            "read": "Look for missing values, weak fields, or quality issues that could affect analysis.",
            "conclusion": "If important fields are incomplete, the business insight may be less reliable.",
            "action": "Fix the weakest data fields before using them for important decisions or reporting.",
        }

    if has_any("order", "orders", "volume", "count"):
        return {
            "question": "How much order activity is the business generating?",
            "read": "Higher order volume shows stronger demand. Drops or unusual spikes should be checked.",
            "conclusion": "Order volume is healthy when it grows without creating delivery, cancellation, or quality problems.",
            "action": "Compare demand growth with delivery and customer quality before scaling further.",
        }

    return {
        "question": "What business signal does this chart show?",
        "read": "Look for the highest values, lowest values, changes over time, and unusual outliers.",
        "conclusion": "The chart highlights where performance is strong, weak, or worth deeper review.",
        "action": "Use the strongest signal to decide what to improve, protect, or investigate next.",
    }



if "show_chart" in globals():
    _minimal_original_show_chart = show_chart

    def show_chart(fig, *args, **kwargs):
        _minimal_original_show_chart(fig, *args, **kwargs)

        try:
            title_obj = getattr(getattr(fig, "layout", None), "title", None)
            title_text = getattr(title_obj, "text", "") if title_obj is not None else ""
            story = _minimal_chart_story_from_title(title_text)

            st.markdown(
                f"""
                <div class="chart-story-card">
                    <div class="chart-story-title">Chart explanation and conclusion</div>
                    <div class="chart-story-body">
                        <b>Business question:</b> {story["question"]}<br>
                        <b>How to read it:</b> {story["read"]}<br>
                        <b>Key conclusion:</b> {story["conclusion"]}<br>
                        <b>Decision action:</b> {story["action"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception:
            return

# MINIMAL_CHART_EXPLANATION_WRAPPER_END


# REAL_KPI_SPARKLINES_SAFE_START

_REAL_KPI_SPARKLINE_MAP = {}
_REAL_KPI_BASE_MARKDOWN = None
_REAL_KPI_CSS_DONE = False

_REAL_KPI_CSS = """
<style>
    .stApp div.metric-card::after {
        content: none !important;
        display: none !important;
        background-image: none !important;
    }

    .stApp div.metric-card {
        padding-bottom: 1.05rem !important;
        cursor: help !important;
    }

    .real-kpi-sparkline {
        margin-top: 0.95rem !important;
        padding-top: 0.72rem !important;
        border-top: 1px solid rgba(148, 163, 184, 0.16) !important;
    }

    .real-kpi-sparkline-head {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        gap: 0.7rem !important;
        margin-bottom: 0.35rem !important;
    }

    .real-kpi-sparkline-label {
        color: #9FB4D9 !important;
        font-size: 0.68rem !important;
        font-weight: 850 !important;
        letter-spacing: 0.10em !important;
        text-transform: uppercase !important;
    }

    .real-kpi-trend-chip {
        padding: 0.2rem 0.46rem !important;
        border-radius: 999px !important;
        font-size: 0.66rem !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        color: #C7D2FE !important;
        border: 1px solid rgba(125, 211, 252, 0.24) !important;
        background: rgba(15, 23, 42, 0.72) !important;
        white-space: nowrap !important;
    }

    .real-kpi-trend-chip.good {
        color: #A7F3D0 !important;
        border-color: rgba(45, 212, 191, 0.30) !important;
        background: rgba(20, 184, 166, 0.12) !important;
    }

    .real-kpi-trend-chip.bad {
        color: #FECACA !important;
        border-color: rgba(251, 113, 133, 0.30) !important;
        background: rgba(244, 63, 94, 0.13) !important;
    }

    .real-kpi-svg {
        width: 100% !important;
        height: 42px !important;
        display: block !important;
        overflow: visible !important;
    }

    .real-kpi-area {
        fill: rgba(125, 211, 252, 0.16) !important;
    }

    .real-kpi-line {
        fill: none !important;
        stroke: #7DD3FC !important;
        stroke-width: 2.5 !important;
        stroke-linecap: round !important;
        stroke-linejoin: round !important;
        filter: drop-shadow(0 0 6px rgba(125, 211, 252, 0.45));
    }

    .real-kpi-dot {
        fill: #F43F5E !important;
        stroke: #FFFFFF !important;
        stroke-width: 1.3 !important;
        filter: drop-shadow(0 0 5px rgba(244, 63, 94, 0.65));
    }

    .stApp div.metric-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(125, 211, 252, 0.46) !important;
        box-shadow: 0 22px 50px rgba(0,0,0,0.36), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    }
</style>
"""


def _rk_find_col(df, names):
    lookup = {str(col).lower(): col for col in df.columns}
    for name in names:
        found = lookup.get(name.lower())
        if found is not None:
            return found
    return None


def _rk_clean(values):
    import math

    out = []
    for value in values:
        try:
            number = float(value)
        except Exception:
            number = 0.0
        if not math.isfinite(number):
            number = 0.0
        out.append(number)
    return out


def _rk_compact(value, prefix="", suffix=""):
    import math

    try:
        value = float(value)
    except Exception:
        return "n/a"

    if not math.isfinite(value):
        return "n/a"

    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000:
        return f"{sign}{prefix}{value / 1_000_000:.2f}M{suffix}"
    if value >= 1_000:
        return f"{sign}{prefix}{value / 1_000:.1f}K{suffix}"
    if suffix == "%":
        return f"{sign}{value:.2f}{suffix}"
    if value >= 100:
        return f"{sign}{prefix}{value:.0f}{suffix}"
    return f"{sign}{prefix}{value:.2f}{suffix}"


def _rk_svg(values, tooltip):
    import html
    import math

    values = _rk_clean(values)
    if len(values) < 2:
        return ""

    width = 160.0
    height = 42.0
    px = 3.0
    py = 5.0

    lo = min(values)
    hi = max(values)

    if math.isclose(lo, hi):
        ys = [height / 2 for _ in values]
    else:
        ys = [py + (hi - value) / (hi - lo) * (height - 2 * py) for value in values]

    step = (width - 2 * px) / max(len(values) - 1, 1)
    points = [(px + idx * step, y) for idx, y in enumerate(ys)]

    line = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    area = line + f" L {points[-1][0]:.2f},{height - py:.2f} L {points[0][0]:.2f},{height - py:.2f} Z"

    last_x, last_y = points[-1]
    safe_tip = html.escape(str(tooltip), quote=True)

    return f"""
    <svg class="real-kpi-svg" viewBox="0 0 160 42" preserveAspectRatio="none" role="img" aria-label="{safe_tip}">
        <title>{safe_tip}</title>
        <path class="real-kpi-area" d="{area}"></path>
        <path class="real-kpi-line" d="{line}"></path>
        <circle class="real-kpi-dot" cx="{last_x:.2f}" cy="{last_y:.2f}" r="3.1"></circle>
    </svg>
    """


def _rk_payload(name, values, labels, direction="up", prefix="", suffix=""):
    import html
    import math

    values = _rk_clean(values)
    if len(values) < 2:
        return ""

    first = values[0]
    last = values[-1]

    if math.isclose(first, 0.0):
        delta = 0.0 if math.isclose(last, 0.0) else 100.0
    else:
        delta = ((last - first) / abs(first)) * 100.0

    good = delta >= 0 if direction == "up" else delta <= 0
    klass = "good" if good else "bad"
    arrow = "↗" if delta >= 0 else "↘"

    start_label = labels[0] if labels else "start"
    end_label = labels[-1] if labels else "latest"

    tooltip = (
        f"{name} real monthly trend | "
        f"{start_label}: {_rk_compact(first, prefix, suffix)} | "
        f"{end_label}: {_rk_compact(last, prefix, suffix)} | "
        f"Change: {delta:+.1f}%"
    )

    svg = _rk_svg(values, tooltip)
    if not svg:
        return ""

    return f"""
    <div class="real-kpi-sparkline" title="{html.escape(tooltip, quote=True)}">
        <div class="real-kpi-sparkline-head">
            <span class="real-kpi-sparkline-label">Real monthly trend</span>
            <span class="real-kpi-trend-chip {klass}">{arrow} {delta:+.1f}%</span>
        </div>
        {svg}
    </div>
    """


def build_real_kpi_sparkline_map(df):
    import pandas as pd

    if df is None or len(df) == 0:
        return {}

    work = df.copy()

    date_col = _rk_find_col(
        work,
        ["order_purchase_timestamp", "order_purchase_date", "purchase_timestamp", "purchase_date", "order_date"],
    )
    if date_col is None:
        return {}

    payment_col = _rk_find_col(work, ["payment_value", "gross_payment_value", "revenue", "total_payment_value"])
    order_col = _rk_find_col(work, ["order_id", "order_unique_id"])
    customer_col = _rk_find_col(work, ["customer_unique_id", "customer_id"])
    status_col = _rk_find_col(work, ["order_status", "status"])
    delivered_col = _rk_find_col(work, ["order_delivered_customer_date", "delivered_customer_date", "actual_delivery_date"])
    estimated_col = _rk_find_col(work, ["order_estimated_delivery_date", "estimated_delivery_date", "promised_delivery_date"])

    work["_rk_month"] = pd.to_datetime(work[date_col], errors="coerce").dt.to_period("M").dt.to_timestamp()
    work = work[work["_rk_month"].notna()].copy()

    if len(work) == 0:
        return {}

    months = pd.Index(sorted(work["_rk_month"].dropna().unique()))[-18:]
    if len(months) < 2:
        return {}

    labels = [pd.Timestamp(month).strftime("%b %Y") for month in months]

    def aligned(series):
        return series.reindex(months, fill_value=0).astype(float).tolist()

    if status_col is not None:
        delivered_mask = work[status_col].astype(str).str.lower().eq("delivered")
    else:
        delivered_mask = pd.Series(True, index=work.index)

    spark = {}

    if payment_col is not None:
        gross = aligned(work.groupby("_rk_month")[payment_col].sum())
        delivered = aligned(work.loc[delivered_mask].groupby("_rk_month")[payment_col].sum())
        leakage = [max(g - d, 0.0) for g, d in zip(gross, delivered)]

        spark["GROSS PAYMENT VALUE"] = _rk_payload("Gross Payment Value", gross, labels, "up", "€")
        spark["DELIVERED REVENUE"] = _rk_payload("Delivered Revenue", delivered, labels, "up", "€")
        spark["REVENUE LEAKAGE"] = _rk_payload("Revenue Leakage", leakage, labels, "down", "€")
    else:
        gross = None

    if order_col is not None:
        order_values = aligned(work.groupby("_rk_month")[order_col].nunique())
    else:
        order_values = aligned(work.groupby("_rk_month").size())

    spark["TOTAL ORDERS"] = _rk_payload("Total Orders", order_values, labels, "up")

    if payment_col is not None:
        aov = [g / o if o else 0.0 for g, o in zip(gross, order_values)]
        spark["AVERAGE GROSS ORDER VALUE"] = _rk_payload("Average Gross Order Value", aov, labels, "up", "€")

    if customer_col is not None:
        customer_values = aligned(work.groupby("_rk_month")[customer_col].nunique())
        spark["UNIQUE CUSTOMERS"] = _rk_payload("Unique Customers", customer_values, labels, "up")

        if order_col is not None:
            customer_orders = (
                work.groupby(["_rk_month", customer_col])[order_col]
                .nunique()
                .reset_index(name="_rk_order_count")
            )
            repeaters = (
                customer_orders[customer_orders["_rk_order_count"] > 1]
                .groupby("_rk_month")[customer_col]
                .nunique()
                .reindex(months, fill_value=0)
                .astype(float)
                .tolist()
            )
            repeat_rate = [
                (repeat / customers * 100.0) if customers else 0.0
                for repeat, customers in zip(repeaters, customer_values)
            ]
            spark["REPEAT CUSTOMER RATE"] = _rk_payload("Repeat Customer Rate", repeat_rate, labels, "up", suffix="%")

    if delivered_col is not None and estimated_col is not None:
        temp = work.copy()
        temp["_rk_delivered"] = pd.to_datetime(temp[delivered_col], errors="coerce")
        temp["_rk_estimated"] = pd.to_datetime(temp[estimated_col], errors="coerce")
        temp = temp[temp["_rk_delivered"].notna() & temp["_rk_estimated"].notna()].copy()

        if len(temp) > 0:
            temp["_rk_late"] = (temp["_rk_delivered"] > temp["_rk_estimated"]).astype(float)
            if order_col is not None:
                late_base = temp[["_rk_month", order_col, "_rk_late"]].drop_duplicates(order_col)
                late_rate = late_base.groupby("_rk_month")["_rk_late"].mean() * 100.0
            else:
                late_rate = temp.groupby("_rk_month")["_rk_late"].mean() * 100.0

            spark["LATE DELIVERY RATE"] = _rk_payload("Late Delivery Rate", aligned(late_rate), labels, "down", suffix="%")

    return {key: value for key, value in spark.items() if value}


def _rk_normalize(text):
    import re

    text = re.sub(r"<.*?>", " ", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.upper().strip()


def _rk_inject(body):
    if not isinstance(body, str):
        return body

    if "metric-card" not in body or "real-kpi-sparkline" in body:
        return body

    normalized = _rk_normalize(body)
    matched_key = None

    for key in sorted(_REAL_KPI_SPARKLINE_MAP.keys(), key=len, reverse=True):
        if key in normalized:
            matched_key = key
            break

    if matched_key is None:
        return body

    sparkline = _REAL_KPI_SPARKLINE_MAP.get(matched_key, "")
    if not sparkline:
        return body

    idx = body.rfind("</div>")
    if idx == -1:
        return body + sparkline

    return body[:idx] + sparkline + body[idx:]


def _rk_markdown_hook(body, *args, **kwargs):
    global _REAL_KPI_CSS_DONE

    if isinstance(body, str) and "metric-card" in body:
        if not _REAL_KPI_CSS_DONE:
            _REAL_KPI_BASE_MARKDOWN(_REAL_KPI_CSS, unsafe_allow_html=True)
            _REAL_KPI_CSS_DONE = True
        body = _rk_inject(body)

    return _REAL_KPI_BASE_MARKDOWN(body, *args, **kwargs)


def setup_real_kpi_sparklines(filtered_df):
    global _REAL_KPI_SPARKLINE_MAP
    global _REAL_KPI_BASE_MARKDOWN
    global _REAL_KPI_CSS_DONE

    _REAL_KPI_SPARKLINE_MAP = build_real_kpi_sparkline_map(filtered_df)

    base = getattr(st, "_real_kpi_base_markdown_safe", st.markdown)
    st.markdown = base
    st._real_kpi_base_markdown_safe = base

    _REAL_KPI_BASE_MARKDOWN = base
    _REAL_KPI_CSS_DONE = False

    st.markdown = _rk_markdown_hook

# REAL_KPI_SPARKLINES_SAFE_END

def main():
    """
    Runs the V5 verified decision-grade Streamlit dashboard.
    """

    # FINAL_AST_SAFE_TOP_START
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 78% 0%, rgba(124, 58, 237, 0.20), transparent 30rem),
                    radial-gradient(circle at 28% 8%, rgba(37, 99, 235, 0.10), transparent 24rem),
                    linear-gradient(180deg, #050B18 0%, #060916 46%, #030712 100%) !important;
            }

            [data-testid="stAppViewContainer"] .main .block-container,
            .main .block-container {
                max-width: 1580px !important;
                padding-top: 0.78rem !important;
            }

            /* Sidebar: sample-style control rail */
            section[data-testid="stSidebar"] {
                background:
                    radial-gradient(circle at 32% 0%, rgba(124, 58, 237, 0.24), transparent 14rem),
                    linear-gradient(180deg, #060B17 0%, #071020 54%, #040816 100%) !important;
                border-right: 1px solid rgba(148, 163, 184, 0.14) !important;
                box-shadow: 18px 0 52px rgba(0, 0, 0, 0.34) !important;
            }

            section[data-testid="stSidebar"] .block-container {
                padding: 0.22rem 0.86rem 1.10rem 0.86rem !important;
            }

            section[data-testid="stSidebar"] .sidebar-card {
                position: relative !important;
                overflow: hidden !important;
                margin: 0.10rem 0 1.05rem 0 !important;
                padding: 1.10rem 1.08rem 1.05rem 1.08rem !important;
                border-radius: 23px !important;
                background:
                    radial-gradient(circle at 92% 0%, rgba(168, 85, 247, 0.50), transparent 8rem),
                    linear-gradient(135deg, rgba(79, 70, 229, 0.78), rgba(88, 28, 135, 0.74)) !important;
                border: 1px solid rgba(196, 181, 253, 0.36) !important;
                box-shadow: 0 18px 44px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.10) !important;
            }

            section[data-testid="stSidebar"] .sidebar-card::before {
                content: "🛒" !important;
                display: grid !important;
                place-items: center !important;
                width: 44px !important;
                height: 44px !important;
                margin-bottom: 0.72rem !important;
                border-radius: 14px !important;
                background: linear-gradient(135deg, rgba(168,85,247,0.66), rgba(59,130,246,0.34)) !important;
                border: 1px solid rgba(221,214,254,0.32) !important;
                color: #FFFFFF !important;
                font-size: 1.34rem !important;
                box-shadow: 0 10px 26px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.14) !important;
            }

            section[data-testid="stSidebar"] .sidebar-card h1,
            section[data-testid="stSidebar"] .sidebar-card h2,
            section[data-testid="stSidebar"] .sidebar-card h3 {
                margin: 0 !important;
                color: #FFFFFF !important;
                font-size: 1.08rem !important;
                line-height: 1.15 !important;
                letter-spacing: -0.035em !important;
                font-weight: 950 !important;
            }

            section[data-testid="stSidebar"] .sidebar-card p {
                margin-top: 0.82rem !important;
                color: #E9D5FF !important;
                font-size: 0.78rem !important;
                line-height: 1.55 !important;
                font-weight: 740 !important;
            }

            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3 {
                color: #F8FAFC !important;
                font-size: 0.95rem !important;
                font-weight: 950 !important;
                letter-spacing: -0.02em !important;
                margin-top: 0.55rem !important;
                margin-bottom: 0.52rem !important;
            }

            section[data-testid="stSidebar"] p {
                color: #C8D4EA !important;
                font-size: 0.78rem !important;
                line-height: 1.5 !important;
                font-weight: 650 !important;
            }

            section[data-testid="stSidebar"] label,
            section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
                color: #DDE7F8 !important;
                font-size: 0.76rem !important;
                font-weight: 850 !important;
            }

            section[data-testid="stSidebar"] [data-baseweb="select"] > div,
            section[data-testid="stSidebar"] [data-testid="stDateInput"] input,
            section[data-testid="stSidebar"] input {
                min-height: 42px !important;
                border-radius: 14px !important;
                background: rgba(15, 23, 42, 0.78) !important;
                border: 1px solid rgba(148, 163, 184, 0.24) !important;
                color: #F8FAFC !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 8px 18px rgba(0,0,0,0.17) !important;
            }

            section[data-testid="stSidebar"] [data-testid="stDateInput"],
            section[data-testid="stSidebar"] [data-testid="stSelectbox"],
            section[data-testid="stSidebar"] [data-testid="stMultiSelect"] {
                padding: 0.52rem 0.56rem 0.68rem 0.56rem !important;
                margin-bottom: 0.58rem !important;
                border-radius: 17px !important;
                background: rgba(15, 23, 42, 0.34) !important;
                border: 1px solid rgba(148, 163, 184, 0.10) !important;
            }

            section[data-testid="stSidebar"] button {
                border-radius: 14px !important;
                border: 1px solid rgba(147, 197, 253, 0.28) !important;
                background: rgba(15, 23, 42, 0.74) !important;
                color: #F8FAFC !important;
                font-weight: 850 !important;
            }

            section[data-testid="stSidebar"] hr {
                margin: 0.80rem 0 !important;
                border: none !important;
                height: 1px !important;
                background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.28), transparent) !important;
            }

            /* Flat sample-style top header */
            .reference-top-shell-v1 {
                position: relative !important;
                margin: 0.05rem 0 1.05rem 0 !important;
                padding: 0.45rem 0 0.45rem 0 !important;
            }

            .reference-top-row-v1 {
                display: grid !important;
                grid-template-columns: minmax(0, 1fr) auto !important;
                align-items: start !important;
                gap: 1.5rem !important;
            }

            .reference-eyebrow-v1 {
                display: inline-flex !important;
                align-items: center !important;
                width: fit-content !important;
                gap: 0.48rem !important;
                padding: 0.50rem 1.02rem !important;
                margin-bottom: 0.86rem !important;
                border-radius: 999px !important;
                background: linear-gradient(180deg, rgba(109, 40, 217, 0.56), rgba(67, 56, 202, 0.42)) !important;
                border: 1px solid rgba(196, 181, 253, 0.36) !important;
                color: #EDE9FE !important;
                font-size: 0.72rem !important;
                font-weight: 950 !important;
                letter-spacing: 0.14em !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.10), 0 12px 30px rgba(0,0,0,0.20) !important;
            }

            .reference-title-v1 {
                color: #FFFFFF !important;
                font-size: clamp(2.65rem, 3.15vw, 4.05rem) !important;
                line-height: 0.98 !important;
                font-weight: 950 !important;
                letter-spacing: -0.065em !important;
                margin: 0 0 0.76rem 0 !important;
                text-shadow: 0 0 30px rgba(96,165,250,0.16) !important;
            }

            .reference-title-v1 span {
                background: linear-gradient(90deg, #FFFFFF, #E3EDFF 46%, #C7DFFF 100%) !important;
                -webkit-background-clip: text !important;
                background-clip: text !important;
                color: transparent !important;
            }

            .reference-subtitle-v1 {
                max-width: 960px !important;
                color: #E2E8F0 !important;
                font-size: 0.98rem !important;
                line-height: 1.55 !important;
                font-weight: 700 !important;
                margin-bottom: 0.05rem !important;
            }

            .reference-date-chip-v1 {
                display: inline-flex !important;
                align-items: center !important;
                gap: 0.72rem !important;
                min-height: 46px !important;
                padding: 0.55rem 0.92rem !important;
                margin-top: 0.12rem !important;
                border-radius: 12px !important;
                background: rgba(9, 14, 29, 0.78) !important;
                border: 1px solid rgba(129, 140, 248, 0.38) !important;
                color: #CFDAF5 !important;
                font-size: 0.92rem !important;
                font-weight: 760 !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 14px 32px rgba(0,0,0,0.22) !important;
                white-space: nowrap !important;
            }

            .reference-date-icon-v1 {
                display: grid !important;
                place-items: center !important;
                width: 36px !important;
                height: 36px !important;
                border-radius: 10px !important;
                background: rgba(67, 56, 202, 0.32) !important;
            }

            /* KPI cards: keep real data and real sparklines */
            .stApp div.metric-card {
                min-height: 214px !important;
                padding: 1.05rem !important;
                border-radius: 16px !important;
                background:
                    radial-gradient(circle at 96% 0%, rgba(129,140,248,0.12), transparent 9rem),
                    linear-gradient(180deg, rgba(20,24,46,0.96), rgba(7,12,25,0.97)) !important;
                border: 1px solid rgba(148,163,184,0.18) !important;
                box-shadow: 0 18px 42px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.06) !important;
                transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease !important;
            }

            .stApp div.metric-card:hover {
                transform: translateY(-2px) !important;
                border-color: rgba(125,211,252,0.42) !important;
                box-shadow: 0 22px 50px rgba(0,0,0,0.36), inset 0 1px 0 rgba(255,255,255,0.08) !important;
            }

            .stApp div.metric-card::after {
                content: none !important;
                display: none !important;
            }

            .real-kpi-sparkline {
                margin-top: 0.78rem !important;
                padding-top: 0.64rem !important;
                border-top: 1px solid rgba(148,163,184,0.15) !important;
            }

            .real-kpi-svg {
                height: 36px !important;
            }

            .stApp [role="tablist"],
            .stApp [role="radiogroup"] {
                border-radius: 16px !important;
                background: linear-gradient(180deg, rgba(20,24,46,0.94), rgba(9,14,29,0.96)) !important;
                border: 1px solid rgba(148,163,184,0.16) !important;
                box-shadow: 0 16px 34px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.05) !important;
                padding: 0.42rem !important;
                gap: 0.35rem !important;
            }

            .stApp [role="tab"],
            .stApp [role="radio"] {
                border-radius: 13px !important;
                color: #CBD5E1 !important;
                font-weight: 800 !important;
            }

            .stApp [role="tab"]:hover,
            .stApp [role="radio"]:hover {
                background: rgba(59,130,246,0.12) !important;
                color: #FFFFFF !important;
            }

            .section-title {
                margin-top: 0.35rem !important;
                margin-bottom: 0.9rem !important;
                font-size: 1.38rem !important;
                letter-spacing: -0.035em !important;
            }

            @media (max-width: 1180px) {
                .reference-top-row-v1 {
                    grid-template-columns: 1fr !important;
                }

                .reference-date-chip-v1 {
                    width: fit-content !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="reference-top-shell-v1"><div class="reference-top-row-v1"><div><div class="reference-eyebrow-v1">♛ EXECUTIVE OVERVIEW</div><div class="reference-title-v1"><span>Ecommerce Performance Intelligence</span></div><div class="reference-subtitle-v1">Decision-grade intelligence for revenue quality, customer behavior, operational reliability, seller performance, payment behavior, and data control.</div></div><div class="reference-date-chip-v1"><span class="reference-date-icon-v1">📅</span><span>2016/09/04 – 2018/10/17</span></div></div></div>""",
        unsafe_allow_html=True,
    )
    # FINAL_AST_SAFE_TOP_END

    try:
        df = load_master_data()
    except Exception as error:
        st.error("Could not load `master_data` from `marketing.db`.")
        st.info("The analytics database could not be prepared automatically.")
        st.exception(error)
        return

    df = prepare_data(df)
    filtered_df = apply_sidebar_filters(df)

    # REAL_KPI_SETUP_SAFE_START
    setup_real_kpi_sparklines(filtered_df)
    # REAL_KPI_SETUP_SAFE_END
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)
    v5_show_executive_kpis(filtered_df)

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
        unsafe_allow_html=True,
    )

    section = st.radio(
        "Choose intelligence module",
        [
            "Executive",
            "Revenue",
            "Customers",
            "Marketing Opportunity",
            "Operations",
            "Products/Sellers",
            "Payments",
            "3D Lab",
            "Data Quality",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if section == "Executive":
        v5_section_brief(
            "Boardroom readout",
            "Start here to separate recorded demand from realized fulfillment. The charts show how gross payment value becomes delivered revenue and where leakage appears.",
        )
        v5_chart_revenue_waterfall(filtered_df)
        v5_chart_monthly_revenue_combo(filtered_df)
        v5_chart_state_category_heatmap(filtered_df)

    elif section == "Revenue":
        v5_section_brief(
            "Revenue intelligence",
            "This section combines revenue momentum, realized fulfillment, geographic concentration, and category concentration.",
        )
        v5_chart_monthly_revenue_combo(filtered_df)
        v5_chart_revenue_waterfall(filtered_df)
        v5_chart_product_treemap(filtered_df)

    elif section == "Customers":
        v5_section_brief(
            "Customer intelligence",
            "This section shows where customer value lives, how concentrated spend is, and which states represent the strongest customer opportunity.",
        )
        v5_chart_customer_frequency(filtered_df)
        v5_chart_customer_value_distribution(filtered_df)
        v5_chart_customer_state_bubble(filtered_df)

    elif section == "Marketing Opportunity":
        v5_section_brief(
            "Marketing opportunity engine",
            "This section exposes high-value states and categories for campaign prioritization, retention plays, assortment work, and pricing experiments.",
        )
        v5_chart_customer_state_bubble(filtered_df)
        v5_chart_category_opportunity_matrix(filtered_df)
        v5_chart_state_category_heatmap(filtered_df)
        v5_chart_category_sunburst(filtered_df)

    elif section == "Operations":
        v5_section_brief(
            "Operations risk pulse",
            "This section connects delivery success, cancellations, unavailable orders, late delivery pressure, and payment leakage to operational risk.",
        )
        v5_show_operations_kpis(filtered_df)
        v5_chart_order_status_donut(filtered_df)
        v5_chart_delivery_delay_distribution(filtered_df)
        v5_chart_late_delivery_heatmap(filtered_df)

    elif section == "Products/Sellers":
        v5_section_brief(
            "Product and seller arena",
            "This section highlights category concentration, seller dependency, and marketplace risk using treemaps, sunburst charts, and risk matrices.",
        )
        v5_chart_product_treemap(filtered_df)
        v5_chart_category_sunburst(filtered_df)
        v5_chart_seller_risk_matrix(filtered_df)

    elif section == "Payments":
        v5_section_brief(
            "Payment intelligence",
            "This section explains payment method value, order volume, AOV, and installment behavior.",
        )
        v5_chart_payment_intelligence(filtered_df)
        v5_chart_installment_profile(filtered_df)

    elif section == "3D Lab":
        v5_section_brief(
            "3D intelligence lab",
            "This section gives enterprise-grade 3D exploration of revenue by time, category, seller volume, cancellation pressure, and gross value.",
        )
        v5_chart_3d_revenue_lab(filtered_df)
        v5_chart_3d_seller_lab(filtered_df)

    elif section == "Data Quality":
        v5_data_quality_control_room(filtered_df)


if __name__ == "__main__":
    main()
