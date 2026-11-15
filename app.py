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

# Import project modules.
# Supports both layouts:
#   1. modules/data_loader.py
#   2. data_loader.py (files directly beside app.py)
import importlib

def load_project_module(module_name):
    """Load a module from the modules package or from the project root."""
    try:
        return importlib.import_module(f"modules.{module_name}")
    except ModuleNotFoundError as exc:
        # Only fall back when the project package/module path is missing.
        # Do not hide missing third-party dependencies inside a module.
        if exc.name not in {"modules", f"modules.{module_name}"}:
            raise
        return importlib.import_module(module_name)


data_loader = load_project_module("data_loader")
data_cleaning = load_project_module("data_cleaning")
sales_analysis = load_project_module("sales_analysis")
product_analysis = load_project_module("product_analysis")
customer_analysis = load_project_module("customer_analysis")
inventory_analysis = load_project_module("inventory_analysis")
recommendations = load_project_module("recommendations")
export_reports = load_project_module("export_reports")

load_sample_datasets = data_loader.load_sample_datasets
merge_datasets = data_loader.merge_datasets
auto_map_columns = data_loader.auto_map_columns
validate_dataset_schema = data_loader.validate_dataset_schema
get_sample_data_dir = data_loader.get_sample_data_dir

generate_data_health_profile = data_cleaning.generate_data_health_profile
clean_dataset_safely = data_cleaning.clean_dataset_safely

filter_sales_data = sales_analysis.filter_sales_data
calculate_sales_kpis = sales_analysis.calculate_sales_kpis
chart_monthly_revenue_trend = sales_analysis.chart_monthly_revenue_trend
chart_daily_revenue_trend = sales_analysis.chart_daily_revenue_trend
chart_sales_by_category_donut = sales_analysis.chart_sales_by_category_donut
chart_top_products_bar = sales_analysis.chart_top_products_bar
chart_revenue_by_category_bar = sales_analysis.chart_revenue_by_category_bar
chart_sales_by_payment = sales_analysis.chart_sales_by_payment
chart_sales_by_region = sales_analysis.chart_sales_by_region
chart_monthly_order_comparison = sales_analysis.chart_monthly_order_comparison

compute_product_performance = product_analysis.compute_product_performance
chart_top_10_products = product_analysis.chart_top_10_products
chart_bottom_10_products = product_analysis.chart_bottom_10_products
chart_product_units_sold = product_analysis.chart_product_units_sold
chart_size_distribution = product_analysis.chart_size_distribution
chart_color_distribution = product_analysis.chart_color_distribution

compute_customer_analytics = customer_analysis.compute_customer_analytics
chart_age_distribution = customer_analysis.chart_age_distribution
chart_gender_distribution = customer_analysis.chart_gender_distribution
chart_customer_segments_donut = customer_analysis.chart_customer_segments_donut
chart_revenue_by_segment = customer_analysis.chart_revenue_by_segment
chart_new_vs_returning = customer_analysis.chart_new_vs_returning
chart_top_10_customers_spend = customer_analysis.chart_top_10_customers_spend

compute_inventory_health = inventory_analysis.compute_inventory_health
chart_stock_by_category = inventory_analysis.chart_stock_by_category
chart_low_stock_products = inventory_analysis.chart_low_stock_products
chart_inventory_distribution = inventory_analysis.chart_inventory_distribution
chart_sales_vs_stock_scatter = inventory_analysis.chart_sales_vs_stock_scatter
chart_category_inventory_value = inventory_analysis.chart_category_inventory_value

generate_business_recommendations = recommendations.generate_business_recommendations
