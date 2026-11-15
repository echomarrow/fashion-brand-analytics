"""
Sales Analytics Module
Calculates sales KPIs, trends, categorical breakdowns, and transaction metrics.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from chart_theme import apply_luxury_theme, LUXURY_PALETTE, BURGUNDY_MONOCHROME

def filter_sales_data(
    df: pd.DataFrame,
    date_preset: str = "All Time",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None,
    categories: Optional[List[str]] = None,
    brands: Optional[List[str]] = None,
    payment_methods: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Applies multi-dimensional filters to sales transactions.
    """
    filtered = df.copy()
    if not np.issubdtype(filtered["Order_Date"].dtype, np.datetime64):
        filtered["Order_Date"] = pd.to_datetime(filtered["Order_Date"], errors="coerce")

    # Determine reference max date in dataset
    max_date = filtered["Order_Date"].max()
    if pd.isna(max_date):
        max_date = datetime.now()

    # Apply date filters
    if date_preset == "Today":
        filtered = filtered[filtered["Order_Date"].dt.date == max_date.date()]
    elif date_preset == "Last 7 Days":
        start = max_date - timedelta(days=7)
        filtered = filtered[filtered["Order_Date"] >= start]
    elif date_preset == "Last 30 Days":
        start = max_date - timedelta(days=30)
        filtered = filtered[filtered["Order_Date"] >= start]
    elif date_preset == "Last 90 Days":
        start = max_date - timedelta(days=90)
        filtered = filtered[filtered["Order_Date"] >= start]
    elif date_preset == "This Year":
        filtered = filtered[filtered["Order_Date"].dt.year == max_date.year]
    elif date_preset == "Custom Date Range" and custom_start and custom_end:
        start_ts = pd.to_datetime(custom_start)
        end_ts = pd.to_datetime(custom_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered = filtered[(filtered["Order_Date"] >= start_ts) & (filtered["Order_Date"] <= end_ts)]

    # Entity dimension filters
    if categories and "All" not in categories and "Category" in filtered.columns:
        filtered = filtered[filtered["Category"].isin(categories)]
        
    if brands and "All" not in brands and "Brand" in filtered.columns:
        filtered = filtered[filtered["Brand"].isin(brands)]

    if payment_methods and "All" not in payment_methods and "Payment_Method" in filtered.columns:
        filtered = filtered[filtered["Payment_Method"].isin(payment_methods)]

    if regions and "All" not in regions and "Region" in filtered.columns:
        filtered = filtered[filtered["Region"].isin(regions)]

    return filtered

def calculate_sales_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes key performance indicators from the active sales data.
    """
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_units": 0,
            "aov": 0.0,
            "total_customers": 0,
            "total_products": 0,
            "avg_daily_revenue": 0.0,
            "revenue_prev_growth": 0.0
        }

    total_revenue = float(df["Total_Amount"].sum())
    total_orders = int(df["Order_ID"].nunique()) if "Order_ID" in df.columns else len(df)
    total_units = int(df["Quantity"].sum()) if "Quantity" in df.columns else len(df)
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    total_customers = int(df["Customer_ID"].nunique()) if "Customer_ID" in df.columns else 0
    total_products = int(df["Product_ID"].nunique()) if "Product_ID" in df.columns else 0

    # Daily velocity
    min_date = df["Order_Date"].min()
    max_date = df["Order_Date"].max()
    days_span = max(1, (max_date - min_date).days + 1)
    avg_daily_revenue = total_revenue / days_span

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_units": total_units,
        "aov": aov,
        "total_customers": total_customers,
        "total_products": total_products,
        "avg_daily_revenue": avg_daily_revenue,
        "days_span": days_span
    }

def chart_monthly_revenue_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly Revenue Trend - Line chart with luxury styling."""
    if df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Monthly Revenue Trend")

    monthly = df.groupby(df["Order_Date"].dt.to_period("M")).agg(
        Revenue=("Total_Amount", "sum"),
        Orders=("Order_ID", "nunique")
    ).reset_index()
    monthly["Period_Str"] = monthly["Order_Date"].astype(str)

    fig = go.Figure()
    # Gradient area fill under curve
    fig.add_trace(go.Scatter(
        x=monthly["Period_Str"],
        y=monthly["Revenue"],
        name="Revenue ($)",
        mode="lines+markers",
        line=dict(color="#722F45", width=3, shape="spline"),
        marker=dict(size=8, color="#4A1F2D", symbol="circle", line=dict(color="#FFFDF9", width=2)),
        fill="tozeroy",
        fillcolor="rgba(114, 47, 69, 0.08)",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Monthly Revenue Trajectory", height=420, legend_position="bottom")
    fig.update_layout(xaxis_title="Billing Month", yaxis_title="Revenue (USD)")
    return fig

def chart_daily_revenue_trend(df: pd.DataFrame) -> go.Figure:
    """Daily revenue trend with rolling 7-day average."""
    if df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Daily Revenue Trend", height=420)

    daily = df.groupby(df["Order_Date"].dt.date).agg(
        Revenue=("Total_Amount", "sum")
    ).reset_index()
    daily["Order_Date"] = pd.to_datetime(daily["Order_Date"])
    daily = daily.sort_values("Order_Date")
    daily["Rolling_7D"] = daily["Revenue"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["Order_Date"],
        y=daily["Revenue"],
        name="Daily Revenue",
        marker_color="rgba(114, 47, 69, 0.35)",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=daily["Order_Date"],
        y=daily["Rolling_7D"],
        name="7-Day Moving Avg",
        line=dict(color="#D69A42", width=3, shape="spline"),
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>7D Avg: $%{y:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Daily Revenue & 7-Day Trendline", height=420, legend_position="bottom")
    fig.update_layout(xaxis_title="Date", yaxis_title="Revenue ($)")
    return fig

def chart_sales_by_category_donut(df: pd.DataFrame) -> go.Figure:
    """Sales by Category - Donut chart with inside percentages and bottom legend."""
    if df.empty or "Category" not in df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Sales by Category", height=420)

    cat_rev = df.groupby("Category")["Total_Amount"].sum().reset_index()
    cat_rev = cat_rev.sort_values("Total_Amount", ascending=False)

    fig = go.Figure(data=[go.Pie(
        labels=cat_rev["Category"],
        values=cat_rev["Total_Amount"],
        hole=0.56,
        marker=dict(colors=LUXURY_PALETTE),
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        insidetextfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )])
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(fig, "Sales Distribution by Category", height=430, legend_position="bottom")
    return fig

def chart_top_products_bar(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """Top N Best-Selling Products - Horizontal Bar chart with full product names."""
    if df.empty or "Product_Name" not in df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, f"Top {n} Best-Selling Products", height=430)

    top_p = df.groupby(["Product_ID", "Product_Name"])["Total_Amount"].sum().reset_index()
    top_p = top_p.sort_values("Total_Amount", ascending=True).tail(n)

    fig = go.Figure(go.Bar(
        x=top_p["Total_Amount"],
        y=top_p["Product_Name"],
        orientation="h",
        marker=dict(
            color=top_p["Total_Amount"],
            colorscale=[[0, "#BA7A92"], [1, "#4A1F2D"]],
            line=dict(color="#FFFDF9", width=1)
        ),
        text=top_p["Total_Amount"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Total Revenue: $%{x:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, f"Top {n} Revenue Generating Products", height=430, show_legend=False, custom_margin=dict(l=220, r=50, t=65, b=55))
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title="")
    return fig

def chart_revenue_by_category_bar(df: pd.DataFrame) -> go.Figure:
    """Revenue by Product Category bar chart."""
    if df.empty or "Category" not in df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Revenue by Category", height=420)

    cat_data = df.groupby("Category").agg(
        Revenue=("Total_Amount", "sum"),
        Units=("Quantity", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    fig = go.Figure(go.Bar(
        x=cat_data["Category"],
        y=cat_data["Revenue"],
        marker_color="#722F45",
        text=cat_data["Revenue"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Revenue by Category", height=430, show_legend=False, custom_margin=dict(l=65, r=35, t=65, b=55))
    fig.update_layout(xaxis_title="Category", yaxis_title="Revenue ($)")
    return fig

def chart_sales_by_payment(df: pd.DataFrame) -> go.Figure:
    """Sales by Payment Method - Donut chart with inside percentages and bottom legend."""
    if df.empty or "Payment_Method" not in df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Payment Method Share", height=420)

    pay_data = df.groupby("Payment_Method")["Total_Amount"].sum().reset_index()

    fig = go.Figure(data=[go.Pie(
        labels=pay_data["Payment_Method"],
        values=pay_data["Total_Amount"],
        hole=0.58,
        marker=dict(colors=LUXURY_PALETTE),
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        insidetextfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Total: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )])
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(fig, "Sales by Payment Method", height=430, legend_position="bottom", custom_margin=dict(l=35, r=35, t=65, b=80))
    return fig

def chart_sales_by_region(df: pd.DataFrame) -> go.Figure:
    """Revenue by Region - Horizontal Bar chart with clean margins."""
    if df.empty or "Region" not in df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Revenue by Region", height=430)

    reg_data = df.groupby("Region")["Total_Amount"].sum().reset_index()
    reg_data = reg_data.sort_values("Total_Amount", ascending=True)

    fig = go.Figure(go.Bar(
        x=reg_data["Total_Amount"],
        y=reg_data["Region"],
        orientation="h",
        marker_color="#43866B",
        text=reg_data["Total_Amount"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y} Region</b><br>Revenue: $%{x:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Geographic Revenue by Region", height=430, show_legend=False, custom_margin=dict(l=90, r=50, t=65, b=55))
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title="")
    return fig

def chart_monthly_order_comparison(df: pd.DataFrame) -> go.Figure:
    """Monthly order volume and average basket size comparison."""
    if df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Monthly Order Volume", height=420)

    monthly = df.groupby(df["Order_Date"].dt.to_period("M")).agg(
        Orders=("Order_ID", "nunique"),
        Units=("Quantity", "sum")
    ).reset_index()
    monthly["Period_Str"] = monthly["Order_Date"].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["Period_Str"],
        y=monthly["Orders"],
        name="Orders Count",
        marker_color="#4A1F2D"
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Period_Str"],
        y=monthly["Units"],
        name="Units Sold",
        mode="lines+markers",
        line=dict(color="#D69A42", width=2),
        yaxis="y2"
    ))

    fig.update_layout(
        yaxis2=dict(
            title="Units Sold",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#D69A42")
        )
    )

    apply_luxury_theme(fig, "Monthly Orders & Units Velocity", height=420, legend_position="bottom")
    fig.update_layout(xaxis_title="Month", yaxis_title="Orders")
    return fig
