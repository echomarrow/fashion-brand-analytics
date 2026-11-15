"""
Product Analytics Module
Evaluates product performance, catalog metrics, size/color breakdowns, and quantile classification.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from modules.chart_theme import apply_luxury_theme, LUXURY_PALETTE, BURGUNDY_MONOCHROME

def compute_product_performance(merged_df: pd.DataFrame, products_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes aggregated performance per product and statistical quartile classification.
    """
    # Group sales by product
    if not merged_df.empty and "Product_ID" in merged_df.columns:
        prod_sales = merged_df.groupby("Product_ID").agg(
            Units_Sold=("Quantity", "sum"),
            Revenue=("Total_Amount", "sum"),
            Orders_Count=("Order_ID", "nunique")
        ).reset_index()
    else:
        prod_sales = pd.DataFrame(columns=["Product_ID", "Units_Sold", "Revenue", "Orders_Count"])

    # Merge with catalog to retain all products (including those with 0 sales)
    perf_df = products_df.merge(prod_sales, on="Product_ID", how="left")
    perf_df["Units_Sold"] = perf_df["Units_Sold"].fillna(0).astype(int)
    perf_df["Revenue"] = perf_df["Revenue"].fillna(0.0).round(2)
    perf_df["Orders_Count"] = perf_df["Orders_Count"].fillna(0).astype(int)

    # Statistical Quantile thresholds for classification
    q75_rev = perf_df["Revenue"].quantile(0.75) if not perf_df.empty else 0
    q25_rev = perf_df["Revenue"].quantile(0.25) if not perf_df.empty else 0
    q75_units = perf_df["Units_Sold"].quantile(0.75) if not perf_df.empty else 0

    def classify(row):
        if row["Revenue"] >= q75_rev or row["Units_Sold"] >= q75_units:
            return "Best Seller"
        elif row["Revenue"] <= q25_rev and row["Units_Sold"] <= perf_df["Units_Sold"].quantile(0.25):
            return "Underperformer"
        else:
            return "Average Performer"

    perf_df["Performance_Status"] = perf_df.apply(classify, axis=1)

    # Summary KPIs
    total_products = len(perf_df)
    
    if not perf_df.empty and perf_df["Revenue"].max() > 0:
        best_rev_row = perf_df.loc[perf_df["Revenue"].idxmax()]
        highest_revenue_prod = f"{best_rev_row['Product_Name']} (${best_rev_row['Revenue']:,.0f})"
        
        best_units_row = perf_df.loc[perf_df["Units_Sold"].idxmax()]
        best_selling_prod = f"{best_units_row['Product_Name']} ({best_units_row['Units_Sold']} units)"
        
        # Lowest seller that is non-zero, or lowest
        lowest_units_row = perf_df.loc[perf_df["Units_Sold"].idxmin()]
        lowest_selling_prod = f"{lowest_units_row['Product_Name']} ({lowest_units_row['Units_Sold']} units)"
    else:
        highest_revenue_prod = "N/A"
        best_selling_prod = "N/A"
        lowest_selling_prod = "N/A"

    kpis = {
        "total_products": total_products,
        "best_selling_product": best_selling_prod,
        "lowest_selling_product": lowest_selling_prod,
        "highest_revenue_product": highest_revenue_prod,
        "q75_revenue_threshold": q75_rev,
        "q25_revenue_threshold": q25_rev,
        "best_sellers_count": int((perf_df["Performance_Status"] == "Best Seller").sum()),
        "underperformers_count": int((perf_df["Performance_Status"] == "Underperformer").sum())
    }

    return perf_df, kpis

def chart_top_10_products(perf_df: pd.DataFrame) -> go.Figure:
    """Top 10 Best-Selling Products by Revenue."""
    if perf_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Top 10 Products by Revenue")

    top10 = perf_df.sort_values("Revenue", ascending=True).tail(10)

    fig = go.Figure(go.Bar(
        x=top10["Revenue"],
        y=top10["Product_Name"],
        orientation="h",
        marker_color="#722F45",
        text=top10["Revenue"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Top 10 Revenue Generating Products", height=420, show_legend=False)
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title="")
    return fig

def chart_bottom_10_products(perf_df: pd.DataFrame) -> go.Figure:
    """Bottom 10 Underperforming Products by Revenue."""
    if perf_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Bottom 10 Underperforming Products", height=420)

    bottom10 = perf_df.sort_values("Revenue", ascending=True).head(10)

    fig = go.Figure(go.Bar(
        x=bottom10["Revenue"],
        y=bottom10["Product_Name"],
        orientation="h",
        marker_color="#C75C5C",
        text=bottom10["Revenue"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Bottom 10 Underperforming Products (Revenue)", height=420, show_legend=False)
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title="")
    return fig

def chart_product_units_sold(perf_df: pd.DataFrame) -> go.Figure:
    """Product-wise units sold across catalog."""
    if perf_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Units Sold by Product", height=420)

    sorted_df = perf_df.sort_values("Units_Sold", ascending=False)

    fig = go.Figure(go.Bar(
        x=sorted_df["Product_Name"],
        y=sorted_df["Units_Sold"],
        marker_color="#4A1F2D",
        hovertemplate="<b>%{x}</b><br>Units Sold: %{y}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Catalog Velocity (Units Sold per Product)", height=420, show_legend=False)
    fig.update_layout(xaxis_tickangle=-45, yaxis_title="Units Sold")
    return fig

def chart_size_distribution(merged_df: pd.DataFrame) -> go.Figure:
    """Size-wise Sales Distribution."""
    if merged_df.empty or "Size" not in merged_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Size Distribution", height=420)

    size_sales = merged_df.groupby("Size").agg(
        Units=("Quantity", "sum"),
        Revenue=("Total_Amount", "sum")
    ).reset_index().sort_values("Units", ascending=False)

    fig = go.Figure(go.Bar(
        x=size_sales["Size"],
        y=size_sales["Units"],
        marker=dict(
            color=size_sales["Units"],
            colorscale=[[0, "#EEDDE2"], [1, "#722F45"]]
        ),
        hovertemplate="<b>Size: %{x}</b><br>Units Sold: %{y}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Size-Wise Demand Distribution", height=420, show_legend=False)
    fig.update_layout(xaxis_title="Size / Fit", yaxis_title="Units Sold")
    return fig

def chart_color_distribution(merged_df: pd.DataFrame) -> go.Figure:
    """Color-wise Sales Distribution."""
    if merged_df.empty or "Color" not in merged_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Color Distribution", height=420)

    color_sales = merged_df.groupby("Color").agg(
        Revenue=("Total_Amount", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    fig = go.Figure(go.Pie(
        labels=color_sales["Color"],
        values=color_sales["Revenue"],
        hole=0.55,
        marker=dict(colors=LUXURY_PALETTE),
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        insidetextfont=dict(family="Plus Jakarta Sans", size=12, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(fig, "Colorway Sales Share", height=430, legend_position="bottom")
    return fig
