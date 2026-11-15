"""
FASHION BRAND ANALYTICS DASHBOARD
A Professional, Interactive Business Intelligence Web Application for Fashion Brands.
Built with Python, Streamlit, Pandas, NumPy, Plotly, OpenPyXL, and ReportLab.
"""

import os
import sys
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import streamlit as st

# Configure page before any other Streamlit commands
st.set_page_config(
    page_title="Fashion Brand Analytics | Executive Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add local directory to path for clean imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import modular project packages
from modules.data_loader import (
    load_sample_datasets,
    merge_datasets,
    auto_map_columns,
    validate_dataset_schema,
    get_sample_data_dir
)
from modules.data_cleaning import (
    generate_data_health_profile,
    clean_dataset_safely
)
from modules.sales_analysis import (
    filter_sales_data,
    calculate_sales_kpis,
    chart_monthly_revenue_trend,
    chart_daily_revenue_trend,
    chart_sales_by_category_donut,
    chart_top_products_bar,
    chart_revenue_by_category_bar,
    chart_sales_by_payment,
    chart_sales_by_region,
    chart_monthly_order_comparison
)
from modules.product_analysis import (
    compute_product_performance,
    chart_top_10_products,
    chart_bottom_10_products,
    chart_product_units_sold,
    chart_size_distribution,
    chart_color_distribution
)
from modules.customer_analysis import (
    compute_customer_analytics,
    chart_age_distribution,
    chart_gender_distribution,
    chart_customer_segments_donut,
    chart_revenue_by_segment,
    chart_new_vs_returning,
    chart_top_10_customers_spend
)
from modules.inventory_analysis import (
    compute_inventory_health,
    chart_stock_by_category,
    chart_low_stock_products,
    chart_inventory_distribution,
    chart_sales_vs_stock_scatter,
    chart_category_inventory_value
)
from modules.recommendations import generate_business_recommendations
from modules.export_reports import (
    generate_csv_bytes,
    generate_excel_analytics_report,
    generate_pdf_summary_report
)

# -------------------------------------------------------------
# 1. LOAD STYLES & INITIALIZE SESSION STATE
# -------------------------------------------------------------
def load_custom_css():
    css_path = os.path.join(current_dir, "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

if "is_demo" not in st.session_state:
    st.session_state.is_demo = True

if "brand_name" not in st.session_state:
    st.session_state.brand_name = "Atelier Royale"

if "student_info" not in st.session_state:
    st.session_state.student_info = {
        "name": "Academic Presentation Candidate",
        "class": "Final Year B.Tech / M.Sc Data Science",
        "department": "Department of Computer Science & AI",
        "college": "College of Engineering & Technology",
        "academic_year": "2025 - 2026"
    }

# Load core datasets if not already in session state
if "sales_df" not in st.session_state or "products_df" not in st.session_state or "customers_df" not in st.session_state:
    sales_init, products_init, customers_init = load_sample_datasets()
    st.session_state.sales_df = sales_init
    st.session_state.products_df = products_init
    st.session_state.customers_df = customers_init
    st.session_state.is_demo = True

# Safe active references
sales_df_raw = st.session_state.sales_df
products_df = st.session_state.products_df
customers_df = st.session_state.customers_df
merged_df_full = merge_datasets(sales_df_raw, products_df, customers_df)

# -------------------------------------------------------------
# 2. SIDEBAR NAVIGATION & GLOBAL CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-title">{st.session_state.brand_name}</div>
        <div class="sidebar-brand-subtitle">Fashion Brand Analytics</div>
        <div class="{ 'badge-demo' if st.session_state.is_demo else 'badge-custom' }">
            {'● DEMO DATA ACTIVE' if st.session_state.is_demo else '● CUSTOM DATA ACTIVE'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation menu
    nav_options = [
        "Dashboard Overview",
        "Sales Analytics",
        "Product Analytics",
        "Customer Analytics",
        "Inventory Analytics",
        "Business Recommendations",
        "Data Management",
        "About Project"
    ]
    nav_icons = ["📊", "📈", "👗", "👥", "📦", "💡", "📁", "ℹ️"]
    nav_display = [f"{icon}  {name}" for icon, name in zip(nav_icons, nav_options)]
    
    selected_page_display = st.radio(
        "NAVIGATION",
        nav_display,
        index=0,
        label_visibility="visible"
    )
    current_page = selected_page_display.split("  ")[1]

    st.markdown("---")

    # Brand customizer in sidebar
    with st.expander("⚙️ Brand & Display Settings", expanded=False):
        new_brand = st.text_input("Brand Name", value=st.session_state.brand_name)
        if new_brand and new_brand != st.session_state.brand_name:
            st.session_state.brand_name = new_brand
            st.rerun()

    # Dynamic date range information
    if not sales_df_raw.empty:
        min_d = sales_df_raw["Order_Date"].min().strftime("%b %d, %Y")
        max_d = sales_df_raw["Order_Date"].max().strftime("%b %d, %Y")
        st.caption(f"📅 **Data Coverage:** {min_d} – {max_d}")
        st.caption(f"📦 **Catalog Volume:** {len(products_df)} SKUs | {len(sales_df_raw):,} Sales")

# -------------------------------------------------------------
# 3. GLOBAL FILTERS (For Analytical Pages)
# -------------------------------------------------------------
analytics_pages = ["Dashboard Overview", "Sales Analytics", "Product Analytics", "Customer Analytics", "Inventory Analytics"]

if current_page in analytics_pages:
    with st.container():
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 1.2, 1.2])
        
        with f_col1:
            date_filter_option = st.selectbox(
                "Date Period",
                ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year", "Custom Date Range"],
                index=0
            )

        with f_col2:
            all_categories = sorted(merged_df_full["Category"].dropna().unique().tolist())
            selected_categories = st.multiselect("Category Filter", ["All"] + all_categories, default=["All"])

        with f_col3:
            all_brands = sorted(merged_df_full["Brand"].dropna().unique().tolist()) if "Brand" in merged_df_full.columns else []
            selected_brands = st.multiselect("Brand Filter", ["All"] + all_brands, default=["All"])

        with f_col4:
            all_regions = sorted(merged_df_full["Region"].dropna().unique().tolist()) if "Region" in merged_df_full.columns else []
            selected_regions = st.multiselect("Region Filter", ["All"] + all_regions, default=["All"])

        custom_start, custom_end = None, None
        if date_filter_option == "Custom Date Range":
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                custom_start = st.date_input("Start Date", value=sales_df_raw["Order_Date"].min().date())
            with d_col2:
                custom_end = st.date_input("End Date", value=sales_df_raw["Order_Date"].max().date())

    # Apply filters dynamically
    active_sales_df = filter_sales_data(
        merged_df_full,
        date_preset=date_filter_option,
        custom_start=custom_start,
        custom_end=custom_end,
        categories=selected_categories,
        brands=selected_brands,
        regions=selected_regions
    )
else:
    active_sales_df = merged_df_full
    date_filter_option = "All Time"

# Pre-calculate active metrics
active_sales_kpis = calculate_sales_kpis(active_sales_df)
perf_df, prod_kpis = compute_product_performance(active_sales_df, products_df)
cust_df, cust_kpis = compute_customer_analytics(active_sales_df, customers_df)
inv_df, inv_kpis = compute_inventory_health(products_df, active_sales_df)
business_recs = generate_business_recommendations(active_sales_df, perf_df, cust_df, inv_df)

# -------------------------------------------------------------
# HELPER: KPI CARD RENDERER
# -------------------------------------------------------------
def render_kpi(label: str, value: str, subtext: str = ""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# PAGE 1: DASHBOARD OVERVIEW
# =============================================================
if current_page == "Dashboard Overview":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Executive Overview</h1>
        <div class="page-subtitle">Real-time performance snapshot across sales velocity, category mix, and key brand drivers.</div>
    </div>
    """, unsafe_allow_html=True)

    # 6 Dynamic KPI Cards (2 rows of 3 for spacious, unclipped luxury typography)
    k_r1_c1, k_r1_c2, k_r1_c3 = st.columns(3)
    with k_r1_c1:
        render_kpi("Total Revenue", f"${active_sales_kpis['total_revenue']:,.2f}", f"Across {active_sales_kpis['days_span']} active days")
    with k_r1_c2:
        render_kpi("Total Orders", f"{active_sales_kpis['total_orders']:,}", "Completed transactions")
    with k_r1_c3:
        render_kpi("Total Units Sold", f"{active_sales_kpis['total_units']:,}", "Apparel units shipped")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    k_r2_c1, k_r2_c2, k_r2_c3 = st.columns(3)
    with k_r2_c1:
        render_kpi("Avg Order Value (AOV)", f"${active_sales_kpis['aov']:,.2f}", "Revenue per completed order")
    with k_r2_c2:
        render_kpi("Active Customers", f"{active_sales_kpis['total_customers']:,}", "Patrons in period")
    with k_r2_c3:
        render_kpi("Catalog Active SKUs", f"{active_sales_kpis['total_products']:,}", f"Out of {len(products_df)} SKUs")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Visualizations Row 1
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        with st.container(border=True):
            st.plotly_chart(chart_monthly_revenue_trend(active_sales_df), use_container_width=True)
    with v_col2:
        with st.container(border=True):
            st.plotly_chart(chart_sales_by_category_donut(active_sales_df), use_container_width=True)

    # Visualizations Row 2
    v_col3, v_col4 = st.columns(2)
    with v_col3:
        with st.container(border=True):
            st.plotly_chart(chart_top_products_bar(active_sales_df, n=5), use_container_width=True)
    with v_col4:
        with st.container(border=True):
            st.plotly_chart(chart_revenue_by_category_bar(active_sales_df), use_container_width=True)

    # Visualizations Row 3
    v_col5, v_col6 = st.columns(2)
    with v_col5:
        with st.container(border=True):
            st.plotly_chart(chart_sales_by_payment(active_sales_df), use_container_width=True)
    with v_col6:
        with st.container(border=True):
            st.plotly_chart(chart_sales_by_region(active_sales_df), use_container_width=True)

    # Recent Transactions Table
    st.markdown("""
    <div class="content-card">
        <div class="content-card-title">Recent Transactions Register</div>
    </div>
    """, unsafe_allow_html=True)

    display_cols = ["Order_ID", "Order_Date", "Customer_Name", "Product_Name", "Category", "Quantity", "Total_Amount", "Payment_Method", "Region"]
    available_cols = [c for c in display_cols if c in active_sales_df.columns]
    
    st.dataframe(
        active_sales_df[available_cols].sort_values("Order_Date", ascending=False).head(20).style.format({
            "Total_Amount": "${:,.2f}",
            "Quantity": "{:,}"
        }),
        use_container_width=True,
        height=320
    )

    # Quick download options
    st.markdown("---")
    exp_c1, exp_c2, exp_c3 = st.columns([1, 1, 2])
    with exp_c1:
        pdf_bytes = generate_pdf_summary_report(
            active_sales_kpis,
            perf_df,
            business_recs,
            brand_name=st.session_state.brand_name,
            date_filter_str=date_filter_option,
            student_info=st.session_state.student_info
        )
        st.download_button(
            "📄 Download Executive PDF Dossier",
            data=pdf_bytes,
            file_name=f"{st.session_state.brand_name.replace(' ', '_')}_Executive_Summary.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with exp_c2:
        excel_bytes = generate_excel_analytics_report(
            active_sales_df,
            perf_df,
            cust_df,
            inv_df,
            business_recs,
            brand_name=st.session_state.brand_name,
            date_filter_str=date_filter_option
        )
        st.download_button(
            "📊 Download Complete Excel Report (.xlsx)",
            data=excel_bytes,
            file_name=f"{st.session_state.brand_name.replace(' ', '_')}_Full_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# =============================================================
# PAGE 2: SALES ANALYTICS
# =============================================================
elif current_page == "Sales Analytics":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Sales Analytics</h1>
        <div class="page-subtitle">Deep dive into gross revenue trajectories, daily velocity, ticket values, and geographic performance.</div>
    </div>
    """, unsafe_allow_html=True)

    # 5 KPI Cards (2 rows for spacious luxury typography)
    s_r1_c1, s_r1_c2, s_r1_c3 = st.columns(3)
    with s_r1_c1:
        render_kpi("Total Revenue", f"${active_sales_kpis['total_revenue']:,.2f}", "Gross sales volume")
    with s_r1_c2:
        render_kpi("Total Orders", f"{active_sales_kpis['total_orders']:,}", "Completed orders")
    with s_r1_c3:
        render_kpi("Average Order Value (AOV)", f"${active_sales_kpis['aov']:,.2f}", "Basket spend per order")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    s_r2_c1, s_r2_c2 = st.columns(2)
    with s_r2_c1:
        render_kpi("Total Units Sold", f"{active_sales_kpis['total_units']:,}", "Garments & accessories shipped")
    with s_r2_c2:
        render_kpi("Avg Daily Revenue", f"${active_sales_kpis['avg_daily_revenue']:,.2f}", f"Over {active_sales_kpis['days_span']} active days")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Analysis Tabs
    sales_tab1, sales_tab2, sales_tab3, sales_tab4, sales_tab5 = st.tabs([
        "📈 Revenue Trends",
        "📦 Order & Volume Analysis",
        "👗 Category Breakdown",
        "🗺️ Regional Performance",
        "📋 Detailed Sales Register"
    ])

    with sales_tab1:
        with st.container(border=True):
            st.plotly_chart(chart_daily_revenue_trend(active_sales_df), use_container_width=True)
        with st.container(border=True):
            st.plotly_chart(chart_monthly_revenue_trend(active_sales_df), use_container_width=True)

    with sales_tab2:
        with st.container(border=True):
            st.plotly_chart(chart_monthly_order_comparison(active_sales_df), use_container_width=True)
        # Quantity by category
        if "Category" in active_sales_df.columns:
            cat_units = active_sales_df.groupby("Category")["Quantity"].sum().reset_index().sort_values("Quantity", ascending=False)
            st.dataframe(
                cat_units.style.format({"Quantity": "{:,} units"}),
                use_container_width=True
            )

    with sales_tab3:
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            with st.container(border=True):
                st.plotly_chart(chart_revenue_by_category_bar(active_sales_df), use_container_width=True)
        with c_col2:
            with st.container(border=True):
                st.plotly_chart(chart_sales_by_category_donut(active_sales_df), use_container_width=True)

    with sales_tab4:
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            with st.container(border=True):
                st.plotly_chart(chart_sales_by_region(active_sales_df), use_container_width=True)
        with r_col2:
            with st.container(border=True):
                st.plotly_chart(chart_sales_by_payment(active_sales_df), use_container_width=True)

    with sales_tab5:
        st.markdown("### Transactional Ledger")
        # Filterable search
        search_query = st.text_input("🔍 Search orders by Order ID, Customer Name, or Product...", "")
        filtered_view = active_sales_df.copy()
        if search_query:
            filtered_view = filtered_view[
                filtered_view["Order_ID"].astype(str).str.contains(search_query, case=False) |
                filtered_view["Customer_Name"].astype(str).str.contains(search_query, case=False) |
                filtered_view["Product_Name"].astype(str).str.contains(search_query, case=False)
            ]

        ledger_cols = ["Order_ID", "Order_Date", "Customer_Name", "Product_Name", "Category", "Quantity", "Unit_Price", "Discount", "Total_Amount", "Payment_Method", "Region"]
        show_cols = [c for c in ledger_cols if c in filtered_view.columns]
        
        st.dataframe(
            filtered_view[show_cols].sort_values("Order_Date", ascending=False).style.format({
                "Unit_Price": "${:,.2f}",
                "Total_Amount": "${:,.2f}",
                "Discount": "{:.1f}%",
                "Quantity": "{:,}"
            }),
            use_container_width=True,
            height=420
        )
        
        st.download_button(
            "📥 Download Filtered Sales Report (CSV)",
            data=generate_csv_bytes(filtered_view[show_cols]),
            file_name="Sales_Report_Filtered.csv",
            mime="text/csv"
        )


# =============================================================
# PAGE 3: PRODUCT ANALYTICS
# =============================================================
elif current_page == "Product Analytics":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Product Performance Analytics</h1>
        <div class="page-subtitle">Granular evaluation of catalog hero styles, underperformers, size runs, and colorway velocity.</div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Product KPIs
    p_kpi_cols = st.columns(4)
    with p_kpi_cols[0]:
        render_kpi("Total Catalog SKUs", f"{prod_kpis['total_products']:,}", "Active fashion products")
    with p_kpi_cols[1]:
        render_kpi("Top Revenue Driver", prod_kpis["highest_revenue_product"], "Highest cumulative revenue")
    with p_kpi_cols[2]:
        render_kpi("Best-Selling SKU", prod_kpis["best_selling_product"], "Highest unit velocity")
    with p_kpi_cols[3]:
        render_kpi("Lowest Velocity SKU", prod_kpis["lowest_selling_product"], "Candidate for clearance review")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Statistical Classification Explanation Card
    with st.expander("ℹ️ Quantile Classification Methodology & Performance Criteria", expanded=False):
        st.markdown(f"""
        **Statistical Segmentation Logic:**
        - **Best Seller (★):** Products generating revenue in the upper quartile (≥ 75th percentile: **${prod_kpis['q75_revenue_threshold']:,.2f}**) OR top 25% unit volume. Total best sellers identified: **{prod_kpis['best_sellers_count']} SKUs**.
        - **Average Performer:** Products with stable velocity situated between the 25th and 75th percentiles.
        - **Underperformer (⚠):** Products in the lower quartile (≤ 25th percentile: **${prod_kpis['q25_revenue_threshold']:,.2f}**) requiring markdown or promotional intervention. Total underperformers identified: **{prod_kpis['underperformers_count']} SKUs**.
        """)

    # Visualizations Row 1: Top 10 vs Bottom 10
    p_row1_c1, p_row1_c2 = st.columns(2)
    with p_row1_c1:
        with st.container(border=True):
            st.plotly_chart(chart_top_10_products(perf_df), use_container_width=True)
    with p_row1_c2:
        with st.container(border=True):
            st.plotly_chart(chart_bottom_10_products(perf_df), use_container_width=True)

    # Visualizations Row 2: Catalog Velocity & Size/Color
    with st.container(border=True):
        st.plotly_chart(chart_product_units_sold(perf_df), use_container_width=True)

    p_row3_c1, p_row3_c2 = st.columns(2)
    with p_row3_c1:
        with st.container(border=True):
            st.plotly_chart(chart_size_distribution(active_sales_df), use_container_width=True)
    with p_row3_c2:
        with st.container(border=True):
            st.plotly_chart(chart_color_distribution(active_sales_df), use_container_width=True)

    # Product Performance Master Table
    st.markdown("### Product Performance Directory")
    
    # Filter by classification status
    status_filter = st.multiselect(
        "Filter by Performance Status",
        ["All", "Best Seller", "Average Performer", "Underperformer"],
        default=["All"]
    )
    
    table_display_df = perf_df.copy()
    if "All" not in status_filter and status_filter:
        table_display_df = table_display_df[table_display_df["Performance_Status"].isin(status_filter)]

    columns_to_show = [
        "Product_ID", "Product_Name", "Category", "Brand", "Size", "Color",
        "Selling_Price", "Units_Sold", "Revenue", "Available_Stock", "Performance_Status"
    ]
    avail_p_cols = [c for c in columns_to_show if c in table_display_df.columns]

    st.dataframe(
        table_display_df[avail_p_cols].sort_values("Revenue", ascending=False).style.format({
            "Selling_Price": "${:,.2f}",
            "Revenue": "${:,.2f}",
            "Units_Sold": "{:,}",
            "Available_Stock": "{:,}"
        }),
        use_container_width=True,
        height=400
    )

    st.download_button(
        "📥 Download Product Analytics Report (CSV)",
        data=generate_csv_bytes(table_display_df[avail_p_cols]),
        file_name="Product_Performance_Report.csv",
        mime="text/csv"
    )


# =============================================================
# PAGE 4: CUSTOMER ANALYTICS
# =============================================================
elif current_page == "Customer Analytics":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Customer Analytics & Segmentation</h1>
        <div class="page-subtitle">Strategic customer lifetime value (LTV), cohort segmentation, retention metrics, and demographic mix.</div>
    </div>
    """, unsafe_allow_html=True)

    # 5 Customer KPIs (2 rows for spacious luxury typography)
    c_r1_c1, c_r1_c2, c_r1_c3 = st.columns(3)
    with c_r1_c1:
        render_kpi("Total Registered Patrons", f"{cust_kpis['total_customers']:,}", "Active customer directory")
    with c_r1_c2:
        render_kpi("New Patrons", f"{cust_kpis['new_customers']:,}", "First acquisition in period")
    with c_r1_c3:
        render_kpi("Returning Patrons", f"{cust_kpis['returning_customers']:,}", "Repeat purchasers (≥ 2 orders)")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    c_r2_c1, c_r2_c2 = st.columns(2)
    with c_r2_c1:
        render_kpi("Average Client Spend (LTV)", f"${cust_kpis['avg_spending']:,.2f}", "Per active patron")
    with c_r2_c2:
        render_kpi("Top VIP Client", cust_kpis["top_customer"], "Highest cumulative spend")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Segmentation Logic Explanation
    with st.expander("ℹ️ RFM Customer Segmentation Methodology & Thresholds", expanded=False):
        st.markdown(f"""
        **Customer Tier Classification Rules:**
        1. **High-Value Customers (VIP):** Repeat buyers (≥ 2 orders) with cumulative spend in top quartile (≥ **${cust_kpis['q75_spend_threshold']:,.2f}**). Count: **{cust_kpis['high_value_count']}**.
        2. **Regular Customers:** Consistent purchasers (≥ 2 orders) with spend between 25th percentile (**${cust_kpis['q25_spend_threshold']:,.2f}**) and 75th percentile. Count: **{cust_kpis['regular_count']}**.
        3. **Occasional Customers:** Single-transaction clients with basket spend above median (**${cust_kpis['q50_spend_threshold']:,.2f}**).
        4. **Low-Value Customers:** Single-order buyers with below-median spend or promotion-only baskets.
        """)

    # Visualizations Row 1: Demographics
    c_row1_c1, c_row1_c2 = st.columns(2)
    with c_row1_c1:
        with st.container(border=True):
            st.plotly_chart(chart_age_distribution(cust_df), use_container_width=True)
    with c_row1_c2:
        with st.container(border=True):
            st.plotly_chart(chart_gender_distribution(cust_df), use_container_width=True)

    # Visualizations Row 2: Segments & Revenue
    c_row2_c1, c_row2_c2 = st.columns(2)
    with c_row2_c1:
        with st.container(border=True):
            st.plotly_chart(chart_customer_segments_donut(cust_df), use_container_width=True)
    with c_row2_c2:
        with st.container(border=True):
            st.plotly_chart(chart_revenue_by_segment(cust_df), use_container_width=True)

    # Visualizations Row 3: New vs Returning & Top 10
    c_row3_c1, c_row3_c2 = st.columns(2)
    with c_row3_c1:
        with st.container(border=True):
            st.plotly_chart(chart_new_vs_returning(cust_df), use_container_width=True)
    with c_row3_c2:
        with st.container(border=True):
            st.plotly_chart(chart_top_10_customers_spend(cust_df), use_container_width=True)

    # Customer Directory Table
    st.markdown("### Client Dossier & Segmentation Registry")
    
    seg_filter = st.multiselect(
        "Filter by Segment",
        ["All", "High-Value Customers", "Regular Customers", "Occasional Customers", "Low-Value Customers"],
        default=["All"]
    )
    
    cust_display = cust_df.copy()
    if "All" not in seg_filter and seg_filter:
        cust_display = cust_display[cust_display["Customer_Segment"].isin(seg_filter)]

    c_cols = ["Customer_ID", "Customer_Name", "Age", "Gender", "Region", "Total_Orders", "Total_Spending", "Customer_Segment", "Customer_Type"]
    valid_c_cols = [c for c in c_cols if c in cust_display.columns]

    st.dataframe(
        cust_display[valid_c_cols].sort_values("Total_Spending", ascending=False).style.format({
            "Total_Spending": "${:,.2f}",
            "Total_Orders": "{:,}",
            "Age": "{:.0f}"
        }),
        use_container_width=True,
        height=380
    )

    st.download_button(
        "📥 Download Customer Analytics Report (CSV)",
        data=generate_csv_bytes(cust_display[valid_c_cols]),
        file_name="Customer_Segmentation_Report.csv",
        mime="text/csv"
    )


# =============================================================
# PAGE 5: INVENTORY ANALYTICS
# =============================================================
elif current_page == "Inventory Analytics":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Inventory Health & Replenishment</h1>
        <div class="page-subtitle">Real-time stock monitoring, stockout risk mitigation, deadstock detection, and replenishment models.</div>
    </div>
    """, unsafe_allow_html=True)

    # Configurable Stock Thresholds Controls
    with st.expander("⚙️ Configure Stock Status Thresholds & Replenishment Parameters", expanded=False):
        thr_col1, thr_col2, thr_col3 = st.columns(3)
        with thr_col1:
            overstock_input = st.slider("Overstocked Threshold (Units)", min_value=50, max_value=250, value=100, step=10)
        with thr_col2:
            lead_time_input = st.slider("Supplier Lead Time (Days)", min_value=5, max_value=45, value=14, step=1)
        with thr_col3:
            safety_days_input = st.slider("Safety Stock Buffer (Days)", min_value=3, max_value=21, value=7, step=1)

    # Recalculate inventory with configured inputs
    inv_df, inv_kpis = compute_inventory_health(
        products_df,
        active_sales_df,
        overstock_threshold=overstock_input,
        lead_time_days=lead_time_input,
        safety_stock_days=safety_days_input
    )

    # 5 Inventory KPIs (2 rows for spacious luxury typography)
    i_r1_c1, i_r1_c2, i_r1_c3 = st.columns(3)
    with i_r1_c1:
        render_kpi("Stock on Hand", f"{inv_kpis['total_stock']:,} units", f"Across {inv_kpis['total_products']} SKUs")
    with i_r1_c2:
        render_kpi("Inventory Retail Value", f"${inv_kpis['inventory_value']:,.2f}", "Holding retail valuation")
    with i_r1_c3:
        render_kpi("Low Stock SKUs", f"{inv_kpis['low_stock_count']}", "At or below reorder level")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    i_r2_c1, i_r2_c2 = st.columns(2)
    with i_r2_c1:
        render_kpi("Out-of-Stock SKUs", f"{inv_kpis['out_of_stock_count']}", "Zero physical inventory")
    with i_r2_c2:
        render_kpi("Overstocked SKUs", f"{inv_kpis['overstocked_count']}", f"Stock > {overstock_input} units")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Charts Row 1: Low stock alerts & Stock by category
    i_row1_c1, i_row1_c2 = st.columns(2)
    with i_row1_c1:
        with st.container(border=True):
            st.plotly_chart(chart_low_stock_products(inv_df), use_container_width=True)
    with i_row1_c2:
        with st.container(border=True):
            st.plotly_chart(chart_stock_by_category(inv_df), use_container_width=True)

    # Charts Row 2: Inventory Distribution & Category Value
    i_row2_c1, i_row2_c2 = st.columns(2)
    with i_row2_c1:
        with st.container(border=True):
            st.plotly_chart(chart_inventory_distribution(inv_df), use_container_width=True)
    with i_row2_c2:
        with st.container(border=True):
            st.plotly_chart(chart_category_inventory_value(inv_df), use_container_width=True)

    # Chart 3: Scatter Sales vs Stock
    with st.container(border=True):
        st.plotly_chart(chart_sales_vs_stock_scatter(inv_df), use_container_width=True)

    # Inventory & Reorder Recommendations Table
    st.markdown("""
    <div class="content-card">
        <div class="content-card-title">Inventory Master Ledger & Replenishment Reorder Guidance</div>
        <p style="font-size: 0.85rem; color: #887F78; margin-top:-4px;">
            *Reorder recommendations are calculated from historical daily velocity, lead times, and safety buffers. Use as decision-support guidance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    inv_filter = st.multiselect(
        "Filter by Stock Status",
        ["All", "Low Stock", "Out of Stock", "In Stock", "Overstocked"],
        default=["All"]
    )

    inv_display = inv_df.copy()
    if "All" not in inv_filter and inv_filter:
        inv_display = inv_display[inv_display["Stock_Status"].isin(inv_filter)]

    inv_table_cols = [
        "Product_ID", "Product_Name", "Category", "Selling_Price", "Units_Sold",
        "Daily_Run_Rate", "Available_Stock", "Reorder_Level", "Stock_Status",
        "Days_Inventory_Remaining", "Suggested_Reorder_Qty", "Inventory_Value"
    ]
    show_inv_cols = [c for c in inv_table_cols if c in inv_display.columns]

    st.dataframe(
        inv_display[show_inv_cols].sort_values(["Stock_Status", "Available_Stock"], ascending=[True, True]).style.format({
            "Selling_Price": "${:,.2f}",
            "Inventory_Value": "${:,.2f}",
            "Daily_Run_Rate": "{:.2f}/day",
            "Units_Sold": "{:,}",
            "Available_Stock": "{:,}",
            "Reorder_Level": "{:,}",
            "Suggested_Reorder_Qty": "{:,}",
            "Days_Inventory_Remaining": "{:.1f} d"
        }),
        use_container_width=True,
        height=400
    )

    st.download_button(
        "📥 Download Inventory & Replenishment Report (CSV)",
        data=generate_csv_bytes(inv_display[show_inv_cols]),
        file_name="Inventory_Replenishment_Report.csv",
        mime="text/csv"
    )


# =============================================================
# PAGE 6: BUSINESS RECOMMENDATIONS
# =============================================================
elif current_page == "Business Recommendations":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Strategic Business Recommendations</h1>
        <div class="page-subtitle">Algorithmic business intelligence engine transforming calculated metrics into prioritized executive actions.</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Grounded Insights Guarantee:** All observations below are algorithmically derived from the active dataset calculations without synthetic claims.")

    rec_c1, rec_c2, rec_c3 = st.columns(3)

    # Section 1: Positive Insights
    with rec_c1:
        st.markdown("### 🌟 Positive Insights")
        for item in business_recs.get("positive_insights", []):
            st.markdown(f"""
            <div class="rec-card-positive">
                <div class="rec-title">{item['title']}</div>
                <div style="font-weight: 600; color: #43866B; font-size: 0.85rem; margin-bottom: 6px;">{item['metric']}</div>
                <div class="rec-body">{item['description']}</div>
                <div style="margin-top: 8px;"><span class="pill-best-seller">{item['tag']}</span></div>
            </div>
            """, unsafe_allow_html=True)
        if not business_recs.get("positive_insights"):
            st.caption("No positive outliers detected in this subset.")

    # Section 2: Areas Requiring Attention
    with rec_c2:
        st.markdown("### ⚠️ Areas Requiring Attention")
        for item in business_recs.get("attention_areas", []):
            st.markdown(f"""
            <div class="rec-card-danger">
                <div class="rec-title">{item['title']}</div>
                <div style="font-weight: 600; color: #C75C5C; font-size: 0.85rem; margin-bottom: 6px;">{item['metric']}</div>
                <div class="rec-body">{item['description']}</div>
                <div style="margin-top: 8px;"><span class="pill-underperformer">{item['tag']}</span></div>
            </div>
            """, unsafe_allow_html=True)
        if not business_recs.get("attention_areas"):
            st.caption("No critical risk areas identified in this subset.")

    # Section 3: Recommended Actions
    with rec_c3:
        st.markdown("### 🎯 Recommended Strategic Actions")
        for item in business_recs.get("recommended_actions", []):
            urgency_color = "#C75C5C" if item.get("urgency") in ["Critical", "High"] else "#D69A42"
            st.markdown(f"""
            <div class="rec-card-warning">
                <div class="rec-title">{item['title']}</div>
                <div style="font-size: 0.78rem; font-weight: 700; color: {urgency_color}; text-transform: uppercase; margin-bottom: 4px;">Priority: {item['urgency']}</div>
                <div class="rec-body"><b>Action:</b> {item['action']}</div>
                <div class="rec-body" style="margin-top: 6px; font-style: italic;"><b>Projected Impact:</b> {item['impact']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Download Executive PDF / Excel
    rec_down_c1, rec_down_c2 = st.columns(2)
    with rec_down_c1:
        pdf_recs = generate_pdf_summary_report(
            active_sales_kpis,
            perf_df,
            business_recs,
            brand_name=st.session_state.brand_name,
            date_filter_str=date_filter_option,
            student_info=st.session_state.student_info
        )
        st.download_button(
            "📄 Export Executive Recommendations Dossier (PDF)",
            data=pdf_recs,
            file_name=f"{st.session_state.brand_name.replace(' ', '_')}_Recommendations_Dossier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with rec_down_c2:
        excel_recs = generate_excel_analytics_report(
            active_sales_df,
            perf_df,
            cust_df,
            inv_df,
            business_recs,
            brand_name=st.session_state.brand_name,
            date_filter_str=date_filter_option
        )
        st.download_button(
            "📊 Export Full Business Intelligence Dossier (Excel)",
            data=excel_recs,
            file_name=f"{st.session_state.brand_name.replace(' ', '_')}_BI_Dossier.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# =============================================================
# PAGE 7: DATA MANAGEMENT & QUALITY
# =============================================================
elif current_page == "Data Management":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">{st.session_state.brand_name} &bull; Data Management & Quality Control</h1>
        <div class="page-subtitle">Upload custom datasets, inspect data hygiene, auto-map columns, apply non-destructive cleaning, and reset demo data.</div>
    </div>
    """, unsafe_allow_html=True)

    dm_tab1, dm_tab2, dm_tab3 = st.tabs([
        "📤 Upload & Ingest Dataset",
        "🩺 Data Quality & Hygiene Diagnostics",
        "🧹 Safe Data Cleaning & Normalization"
    ])

    # ---------------- TAB 1: UPLOAD ----------------
    with dm_tab1:
        st.markdown("### Upload Fashion Business Datasets")
        st.write("Upload your sales transactions, product catalog, or customer records in **CSV** or **Excel** (`.xlsx`, `.xls`) format.")

        target_entity = st.selectbox(
            "Select Target Entity for Upload",
            ["Sales Transactions (sales.csv)", "Product Catalog (products.csv)", "Customer Directory (customers.csv)"],
            index=0
        )

        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            key="custom_file_uploader"
        )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    raw_uploaded_df = pd.read_csv(uploaded_file)
                else:
                    raw_uploaded_df = pd.read_excel(uploaded_file)
                    
                st.success(f"Successfully read **{uploaded_file.name}** ({len(raw_uploaded_df):,} rows, {len(raw_uploaded_df.columns)} columns)")

                # Entity mapping
                entity_key = "sales" if "Sales" in target_entity else ("products" if "Product" in target_entity else "customers")
                
                # Auto-mapping
                mapped_df, mapping_dict = auto_map_columns(raw_uploaded_df, entity_key)

                st.markdown("#### Schema & Column Mapping")
                st.caption("Our smart mapper detects variations in column names (e.g., 'Order Date' -> 'Order_Date'). You can adjust below:")

                # Manual override columns
                map_cols = st.columns(3)
                final_mapping = {}
                col_idx = 0
                for orig_col in raw_uploaded_df.columns:
                    current_mapped = mapping_dict.get(orig_col, orig_col)
                    with map_cols[col_idx % 3]:
                        user_target = st.text_input(f"Map '{orig_col}' to:", value=current_mapped, key=f"map_{orig_col}")
                        final_mapping[orig_col] = user_target
                    col_idx += 1

                applied_df = raw_uploaded_df.rename(columns=final_mapping)

                # Validation
                is_valid, missing_reqs = validate_dataset_schema(applied_df, entity_key)

                if is_valid:
                    st.success(f"✅ Schema validation passed! All required {entity_key.upper()} columns are present.")
                else:
                    st.warning(f"⚠️ Missing recommended columns for {entity_key}: {', '.join(missing_reqs)}. You can still use the dataset, but some charts may use defaults.")

                st.markdown("#### Dataset Preview")
                st.dataframe(applied_df.head(10), use_container_width=True)

                if st.button("🚀 Load Uploaded Dataset into Active Analytics", key="apply_upload_btn"):
                    if entity_key == "sales":
                        if "Order_Date" in applied_df.columns:
                            applied_df["Order_Date"] = pd.to_datetime(applied_df["Order_Date"], errors="coerce")
                        st.session_state.sales_df = applied_df
                    elif entity_key == "products":
                        st.session_state.products_df = applied_df
                    else:
                        st.session_state.customers_df = applied_df
                        
                    st.session_state.is_demo = False
                    st.success(f"Custom {entity_key.capitalize()} dataset successfully activated! All dashboard metrics updated.")
                    st.rerun()

            except Exception as e:
                st.error(f"Error parsing file: {e}")

        st.markdown("---")
        st.markdown("### Sample Datasets & Demo Reset")
        sample_c1, sample_c2 = st.columns(2)
        
        with sample_c1:
            # Download sample Excel
            sample_excel_path = os.path.join(get_sample_data_dir(), "fashion_brand_demo.xlsx")
            if os.path.exists(sample_excel_path):
                with open(sample_excel_path, "rb") as sf:
                    st.download_button(
                        "📥 Download Sample Fashion Dataset (Excel)",
                        data=sf.read(),
                        file_name="Fashion_Brand_Sample_Data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        with sample_c2:
            if st.button("🔄 Reset to Default Demo Dataset", use_container_width=True):
                s_init, p_init, c_init = load_sample_datasets()
                st.session_state.sales_df = s_init
                st.session_state.products_df = p_init
                st.session_state.customers_df = c_init
                st.session_state.is_demo = True
                st.success("Successfully reset to verified demo dataset.")
                st.rerun()

    # ---------------- TAB 2: DIAGNOSTICS ----------------
    with dm_tab2:
        st.markdown("### Comprehensive Data Quality Audit")
        
        audit_dataset_choice = st.selectbox(
            "Select Active Dataset to Audit",
            ["Sales Transactions", "Product Catalog", "Customer Directory"]
        )
        
        target_df = st.session_state.sales_df if "Sales" in audit_dataset_choice else (
            st.session_state.products_df if "Product" in audit_dataset_choice else st.session_state.customers_df
        )

        health_profile = generate_data_health_profile(target_df, audit_dataset_choice)

        score_c1, score_c2, score_c3 = st.columns([1, 1, 1])
        with score_c1:
            st.metric("Overall Health Score", f"{health_profile['health_score']} / 100")
        with score_c2:
            st.metric("Total Records", f"{health_profile['total_rows']:,}")
        with score_c3:
            st.metric("Duplicate Rows", f"{health_profile['duplicate_rows']:,}")

        st.markdown("#### Missing Values & Column Types")
        st.dataframe(health_profile["missing_summary"], use_container_width=True)

        st.markdown("#### Anomaly & Invalid Value Checks")
        if health_profile["invalid_checks"]:
            inv_df_report = pd.DataFrame(health_profile["invalid_checks"])
            st.dataframe(inv_df_report, use_container_width=True)
        else:
            st.success("✅ No negative values, invalid ages, or corrupt date records found in this dataset.")

    # ---------------- TAB 3: CLEANING ----------------
    with dm_tab3:
        st.markdown("### Interactive Safe Data Cleaner")
        st.write("Apply verified non-destructive cleaning transformations to the active dataset.")

        clean_choice = st.selectbox(
            "Choose Dataset to Clean",
            ["Sales Transactions", "Product Catalog", "Customer Directory"],
            key="clean_choice_sel"
        )
        clean_target_df = st.session_state.sales_df if "Sales" in clean_choice else (
            st.session_state.products_df if "Product" in clean_choice else st.session_state.customers_df
        )

        cl_c1, cl_c2 = st.columns(2)
        with cl_c1:
            opt_dedup = st.checkbox("Remove duplicate rows", value=True)
            opt_neg = st.checkbox("Convert negative values to absolute positive", value=True)
        with cl_c2:
            opt_num_impute = st.selectbox("Fill missing numeric values with", ["median", "mean", "zero"])
            opt_cat_impute = st.selectbox("Fill missing categorical values with", ["mode", "Unknown"])

        if st.button("🧹 Run Safe Cleaning Process"):
            cleaned_result_df, audit_info = clean_dataset_safely(
                clean_target_df,
                remove_duplicates=opt_dedup,
                fill_missing_numeric=opt_num_impute,
                fill_missing_categorical=opt_cat_impute,
                filter_negative_values=opt_neg
            )
            
            st.success(f"Data cleaning finished! Rows retained: {audit_info['final_rows']} (Removed {audit_info['rows_removed']} rows)")
            
            if audit_info["changelog"]:
                st.markdown("**Modifications Applied:**")
                for chg in audit_info["changelog"]:
                    st.write(f"- {chg}")
            else:
                st.info("No modifications were necessary; dataset is already clean.")

            # Store back
            if "Sales" in clean_choice:
                st.session_state.sales_df = cleaned_result_df
            elif "Product" in clean_choice:
                st.session_state.products_df = cleaned_result_df
            else:
                st.session_state.customers_df = cleaned_result_df

            st.download_button(
                "📥 Download Cleaned Dataset (CSV)",
                data=generate_csv_bytes(cleaned_result_df),
                file_name=f"Cleaned_{clean_choice.replace(' ', '_')}.csv",
                mime="text/csv"
            )


# =============================================================
# PAGE 8: ABOUT PROJECT
# =============================================================
elif current_page == "About Project":
    st.markdown(f"""
    <div class="page-header-container">
        <h1 class="page-title">About the Project</h1>
        <div class="page-subtitle">Fashion Brand Analytics &bull; Data-Driven Insights for Better Business Decisions.</div>
    </div>
    """, unsafe_allow_html=True)

    about_c1, about_c2 = st.columns([1.5, 1.2])

    with about_c1:
        st.markdown("""
        ### Project Objective
        **Fashion Brand Analytics** is an advanced Business Intelligence and Decision Support System engineered to transform raw, fragmented retail data into actionable strategic insights.

        By bridging the gap between raw transaction ledgers and executive decision-making, this system addresses critical business challenges:
        - Identifying high-margin hero products and underperforming lines.
        - Segmenting patrons via quantitative RFM-inspired behavioral models.
        - Automating stock replenishment alerts to prevent costly out-of-stock leakages.
        - Uncovering regional demand variances and seasonal sales momentum.
        """)

        st.markdown("""
        ### End-to-End Analytical Workflow
        ```
        ┌──────────────┐     ┌───────────────┐     ┌────────────────┐
        │   RAW DATA   │ ──> │ DATA CLEANING │ ──> │ DATA ANALYSIS  │
        └──────────────┐     └───────────────┘     └────────────────┘
                                                            │
                                                            ▼
        ┌──────────────┐     ┌───────────────┐     ┌────────────────┐
        │ RECOMMEND-   │ <── │   BUSINESS    │ <── │ VISUALIZATION  │
        │    ATIONS    │     │   INSIGHTS    │     │  & DASHBOARD   │
        └──────────────┘     └───────────────┘     └────────────────┘
        ```
        """)

        st.markdown("""
        ### Project Architecture & Modules
        1. **Sales Analytics:** Revenue trajectories, order volume, daily velocity, payment gateway distributions.
        2. **Product Analytics:** Quartile classification (Best Seller vs Underperformer), color & size-run velocity.
        3. **Customer Analytics:** Demographic cohorts, retention, VIP customer lifetime value (LTV).
        4. **Inventory Analytics:** Real-time stock status, holding valuation, days of inventory remaining (DOIR), replenishment modeling.
        5. **Business Recommendations:** Multi-factor algorithmic engine generating genuine, data-grounded strategic actions.
        6. **Data Management:** File uploads, column fuzzy mapping, hygiene diagnostics, and non-destructive cleaning.
        """)

    with about_c2:
        st.markdown("""
        ### Technology Stack
        - **Python 3.13:** Core analytical runtime and data processing.
        - **Streamlit:** Interactive web application framework & reactive dashboard.
        - **Pandas & NumPy:** In-memory vector transformations, joins, and quantile statistical modeling.
        - **Plotly:** Bespoke interactive charts rendered with editorial luxury styling.
        - **OpenPyXL:** Multi-tab formatted Excel workbook generation with styled headers and borders.
        - **ReportLab:** Direct PDF compilation of executive summary dossiers with sign-off blocks.
        """)

        st.markdown("### Academic Candidate Information")
        st.caption("Update student presentation details below to personalize exported dossiers and reports:")
        
        stud_name = st.text_input("Student Name", value=st.session_state.student_info["name"])
        stud_class = st.text_input("Class / Course", value=st.session_state.student_info["class"])
        stud_dept = st.text_input("Department", value=st.session_state.student_info["department"])
        stud_college = st.text_input("College / University", value=st.session_state.student_info["college"])
        stud_year = st.text_input("Academic Year", value=st.session_state.student_info["academic_year"])

        if st.button("💾 Save Presentation Information"):
            st.session_state.student_info = {
                "name": stud_name,
                "class": stud_class,
                "department": stud_dept,
                "college": stud_college,
                "academic_year": stud_year
            }
            st.success("Student details saved! All exported PDF dossiers will reflect this information.")
