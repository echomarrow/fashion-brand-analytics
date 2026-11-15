"""
Automated Verification & Unit Test Suite for Fashion Brand Analytics
Tests data loading, metrics calculation, chart generation, Excel & PDF exports, and data cleaning.
"""

import os
import sys

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from modules.data_loader import load_sample_datasets, merge_datasets, auto_map_columns, validate_dataset_schema
from modules.sales_analysis import filter_sales_data, calculate_sales_kpis, chart_monthly_revenue_trend, chart_daily_revenue_trend
from modules.product_analysis import compute_product_performance, chart_top_10_products, chart_product_units_sold
from modules.customer_analysis import compute_customer_analytics, chart_customer_segments_donut, chart_age_distribution
from modules.inventory_analysis import compute_inventory_health, chart_low_stock_products, chart_sales_vs_stock_scatter
from modules.recommendations import generate_business_recommendations
from modules.export_reports import generate_csv_bytes, generate_excel_analytics_report, generate_pdf_summary_report
from modules.data_cleaning import generate_data_health_profile, clean_dataset_safely

def run_all_tests():
    print("=" * 60)
    print("RUNNING FASHION BRAND ANALYTICS VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test Data Loading
    print("\n[Test 1] Loading sample datasets...")
    sales_df, products_df, customers_df = load_sample_datasets()
    assert len(sales_df) >= 1000, f"Sales rows < 1000: {len(sales_df)}"
    assert len(products_df) >= 30, f"Products rows < 30: {len(products_df)}"
    assert len(customers_df) >= 100, f"Customers rows < 100: {len(customers_df)}"
    print(f" -> PASSED: Sales ({len(sales_df)}), Products ({len(products_df)}), Customers ({len(customers_df)})")

    # 2. Test Merging
    print("\n[Test 2] Testing relational dataset merging...")
    merged_df = merge_datasets(sales_df, products_df, customers_df)
    assert len(merged_df) == len(sales_df), f"Merged length mismatch: {len(merged_df)} vs {len(sales_df)}"
    assert "Category" in merged_df.columns
    assert "Customer_Name" in merged_df.columns
    print(f" -> PASSED: Merged DataFrame contains {len(merged_df)} rows and {len(merged_df.columns)} columns.")

    # 3. Test Sales Analytics
    print("\n[Test 3] Testing Sales KPIs and Filtering...")
    filtered_30d = filter_sales_data(merged_df, date_preset="Last 30 Days")
    kpis = calculate_sales_kpis(filtered_30d)
    assert kpis["total_revenue"] > 0
    assert kpis["total_orders"] > 0
    assert kpis["aov"] > 0
    print(f" -> PASSED: 30D Revenue: ${kpis['total_revenue']:,.2f}, Orders: {kpis['total_orders']}, AOV: ${kpis['aov']:,.2f}")

    # Test Charts
    fig_line = chart_monthly_revenue_trend(merged_df)
    fig_daily = chart_daily_revenue_trend(merged_df)
    assert fig_line is not None and fig_daily is not None
    print(" -> PASSED: Sales Plotly figures compiled successfully.")

    # 4. Test Product Analytics
    print("\n[Test 4] Testing Product Performance & Quartile Status...")
    perf_df, prod_kpis = compute_product_performance(merged_df, products_df)
    assert len(perf_df) == len(products_df)
    assert "Performance_Status" in perf_df.columns
    status_counts = perf_df["Performance_Status"].value_counts().to_dict()
    print(f" -> PASSED: Products classified: {status_counts}")
    assert "Best Seller" in status_counts
    fig_p10 = chart_top_10_products(perf_df)
    assert fig_p10 is not None

    # 5. Test Customer Analytics
    print("\n[Test 5] Testing Customer RFM Segmentation...")
    cust_df, cust_kpis = compute_customer_analytics(merged_df, customers_df)
    assert len(cust_df) == len(customers_df)
    assert "Customer_Segment" in cust_df.columns
    seg_counts = cust_df["Customer_Segment"].value_counts().to_dict()
    print(f" -> PASSED: Customer Segments: {seg_counts}")
    assert "High-Value Customers" in seg_counts
    fig_cust = chart_customer_segments_donut(cust_df)
    assert fig_cust is not None

    # 6. Test Inventory Analytics
    print("\n[Test 6] Testing Inventory Replenishment Engine...")
    inv_df, inv_kpis = compute_inventory_health(products_df, merged_df)
    assert len(inv_df) == len(products_df)
    assert "Stock_Status" in inv_df.columns
    assert "Suggested_Reorder_Qty" in inv_df.columns
    stock_counts = inv_df["Stock_Status"].value_counts().to_dict()
    print(f" -> PASSED: Stock Statuses: {stock_counts}")
    assert inv_kpis["low_stock_count"] > 0 or inv_kpis["out_of_stock_count"] > 0
    fig_stock = chart_low_stock_products(inv_df)
    assert fig_stock is not None

    # 7. Test Business Recommendations
    print("\n[Test 7] Testing Business Recommendations Engine...")
    recs = generate_business_recommendations(merged_df, perf_df, cust_df, inv_df)
    assert len(recs["positive_insights"]) > 0, "No positive insights generated!"
    assert len(recs["attention_areas"]) > 0, "No risk areas identified!"
    assert len(recs["recommended_actions"]) > 0, "No recommendations generated!"
    print(f" -> PASSED: Generated {len(recs['positive_insights'])} Positive Insights, "
          f"{len(recs['attention_areas'])} Areas for Attention, and "
          f"{len(recs['recommended_actions'])} Strategic Actions.")

    # 8. Test Data Quality & Cleaning
    print("\n[Test 8] Testing Data Hygiene Audit & Cleaning...")
    health = generate_data_health_profile(sales_df, "Sales")
    assert 0 <= health["health_score"] <= 100
    cleaned_df, audit = clean_dataset_safely(sales_df)
    assert len(cleaned_df) <= len(sales_df)
    print(f" -> PASSED: Data Health Score: {health['health_score']}/100. Cleaning applied: {len(audit['changelog'])} items.")

    # 9. Test Excel Export
    print("\n[Test 9] Testing Multi-Sheet Formatted Excel Export...")
    excel_bytes = generate_excel_analytics_report(
        merged_df, perf_df, cust_df, inv_df, recs,
        brand_name="Atelier Royale", date_filter_str="All Time"
    )
    assert len(excel_bytes) > 5000, f"Excel file too small: {len(excel_bytes)} bytes"
    print(f" -> PASSED: Excel workbook generated ({len(excel_bytes):,} bytes).")

    # 10. Test PDF Export
    print("\n[Test 10] Testing Executive PDF Summary Dossier...")
    student_info = {
        "name": "Sarah Jenkins",
        "class": "Final Year Data Science",
        "department": "Computer Science & Engineering",
        "college": "Oxford Institute of Technology"
    }
    pdf_bytes = generate_pdf_summary_report(
        kpis, perf_df, recs,
        brand_name="Atelier Royale",
        date_filter_str="All Time",
        student_info=student_info
    )
    assert len(pdf_bytes) > 2000, f"PDF file too small: {len(pdf_bytes)} bytes"
    assert pdf_bytes.startswith(b"%PDF"), "Generated bytes do not start with %PDF header!"
    print(f" -> PASSED: Executive PDF generated ({len(pdf_bytes):,} bytes) with valid %PDF header.")

    print("\n" + "=" * 60)
    print("ALL 10 TESTS PASSED SUCCESSFULLY! APPLICATION IS FULLY FUNCTIONAL.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
