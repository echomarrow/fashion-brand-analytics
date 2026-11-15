"""
Customer Analytics Module
Analyzes demographic distributions, customer lifetime spend, cohort behavior, and RFM-style segmentation.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from modules.chart_theme import apply_luxury_theme, LUXURY_PALETTE

def compute_customer_analytics(merged_df: pd.DataFrame, customers_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes individual customer behavior metrics and classifies into strategic customer segments.
    """
    if not merged_df.empty and "Customer_ID" in merged_df.columns:
        cust_orders = merged_df.groupby("Customer_ID").agg(
            Total_Orders=("Order_ID", "nunique"),
            Total_Spending=("Total_Amount", "sum"),
            Total_Units=("Quantity", "sum"),
            First_Order=("Order_Date", "min"),
            Last_Order=("Order_Date", "max")
        ).reset_index()
    else:
        cust_orders = pd.DataFrame(columns=["Customer_ID", "Total_Orders", "Total_Spending", "Total_Units", "First_Order", "Last_Order"])

    # Merge with demographic customer directory
    analysis_df = customers_df.merge(cust_orders, on="Customer_ID", how="left")
    analysis_df["Total_Orders"] = analysis_df["Total_Orders"].fillna(0).astype(int)
    analysis_df["Total_Spending"] = analysis_df["Total_Spending"].fillna(0.0).round(2)
    analysis_df["Total_Units"] = analysis_df["Total_Units"].fillna(0).astype(int)

    # Calculate Segmentation Thresholds
    # Active buyers only for percentile thresholds
    active_mask = analysis_df["Total_Spending"] > 0
    active_spends = analysis_df.loc[active_mask, "Total_Spending"]

    q75_spend = active_spends.quantile(0.75) if not active_spends.empty else 1500.0
    q50_spend = active_spends.quantile(0.50) if not active_spends.empty else 800.0
    q25_spend = active_spends.quantile(0.25) if not active_spends.empty else 400.0

    def assign_segment(row):
        orders = row["Total_Orders"]
        spend = row["Total_Spending"]
        
        if orders >= 2 and spend >= q75_spend:
            return "High-Value Customers"
        elif orders >= 2 and spend >= q25_spend:
            return "Regular Customers"
        elif orders >= 1 and spend >= q50_spend:
            return "Occasional Customers"
        else:
            return "Low-Value Customers"

    analysis_df["Customer_Segment"] = analysis_df.apply(assign_segment, axis=1)

    # Customer classification: New vs Returning (>= 2 orders is returning)
    analysis_df["Customer_Type"] = analysis_df["Total_Orders"].apply(
        lambda o: "Returning Customer" if o >= 2 else ("New Customer" if o == 1 else "Inactive")
    )

    # High-level KPIs
    total_customers = len(analysis_df)
    returning_count = int((analysis_df["Total_Orders"] >= 2).sum())
    new_count = int((analysis_df["Total_Orders"] == 1).sum())
    active_count = returning_count + new_count
    
    avg_customer_spend = float(analysis_df["Total_Spending"].sum() / active_count) if active_count > 0 else 0.0

    if not analysis_df.empty and analysis_df["Total_Spending"].max() > 0:
        top_row = analysis_df.loc[analysis_df["Total_Spending"].idxmax()]
        top_customer_name = f"{top_row['Customer_Name']} (${top_row['Total_Spending']:,.2f})"
    else:
        top_customer_name = "N/A"

    kpis = {
        "total_customers": total_customers,
        "new_customers": new_count,
        "returning_customers": returning_count,
        "avg_spending": avg_customer_spend,
        "top_customer": top_customer_name,
        "q75_spend_threshold": q75_spend,
        "q50_spend_threshold": q50_spend,
        "q25_spend_threshold": q25_spend,
        "high_value_count": int((analysis_df["Customer_Segment"] == "High-Value Customers").sum()),
        "regular_count": int((analysis_df["Customer_Segment"] == "Regular Customers").sum())
    }

    return analysis_df, kpis

def chart_age_distribution(cust_df: pd.DataFrame) -> go.Figure:
    """Customer Age Distribution histogram."""
    if cust_df.empty or "Age" not in cust_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Age Distribution")

    fig = go.Figure(go.Histogram(
        x=cust_df["Age"],
        nbinsx=12,
        marker_color="#722F45",
        marker_line=dict(color="#FFFDF9", width=1.5),
        hovertemplate="Age Bracket: %{x}<br>Count: %{y}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Customer Age Distribution", height=420, show_legend=False)
    fig.update_layout(xaxis_title="Age (Years)", yaxis_title="Customer Count")
    return fig

def chart_gender_distribution(cust_df: pd.DataFrame) -> go.Figure:
    """Gender Distribution Donut chart."""
    if cust_df.empty or "Gender" not in cust_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Gender Breakdown", height=420)

    gender_data = cust_df["Gender"].value_counts().reset_index()
    gender_data.columns = ["Gender", "Count"]

    fig = go.Figure(go.Pie(
        labels=gender_data["Gender"],
        values=gender_data["Count"],
        hole=0.56,
        marker=dict(colors=["#722F45", "#43866B", "#D69A42"]),
        textinfo="percent",
        textposition="inside",
        insidetextfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(fig, "Customer Demographics by Gender", height=430, legend_position="bottom")
    return fig

def chart_customer_segments_donut(cust_df: pd.DataFrame) -> go.Figure:
    """Customer Segments breakdown."""
    if cust_df.empty or "Customer_Segment" not in cust_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Customer Segmentation", height=430)

    seg_data = cust_df["Customer_Segment"].value_counts().reset_index()
    seg_data.columns = ["Segment", "Count"]

    palette = ["#722F45", "#D69A42", "#43866B", "#887F78"]

    fig = go.Figure(go.Pie(
        labels=seg_data["Segment"],
        values=seg_data["Count"],
        hole=0.56,
        marker=dict(colors=palette),
        textinfo="percent",
        textposition="inside",
        insidetextfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(fig, "Customer Segmentation Composition", height=430, legend_position="bottom")
    return fig

def chart_revenue_by_segment(cust_df: pd.DataFrame) -> go.Figure:
    """Revenue contribution per customer segment."""
    if cust_df.empty or "Customer_Segment" not in cust_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Revenue by Segment", height=430)

    rev_seg = cust_df.groupby("Customer_Segment")["Total_Spending"].sum().reset_index()
    rev_seg = rev_seg.sort_values("Total_Spending", ascending=False)

    fig = go.Figure(go.Bar(
        x=rev_seg["Customer_Segment"],
        y=rev_seg["Total_Spending"],
        marker_color=["#722F45", "#D69A42", "#43866B", "#887F78"][:len(rev_seg)],
        text=rev_seg["Total_Spending"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Total Contribution: $%{y:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Revenue Contribution by Segment", height=430, show_legend=False)
    fig.update_layout(xaxis_title="", yaxis_title="Revenue ($)")
    return fig

def chart_new_vs_returning(cust_df: pd.DataFrame) -> go.Figure:
    """New vs Returning Customers Revenue and Count."""
    if cust_df.empty or "Customer_Type" not in cust_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "New vs Returning", height=430)

    type_data = cust_df[cust_df["Customer_Type"] != "Inactive"].groupby("Customer_Type").agg(
        Count=("Customer_ID", "count"),
        Spending=("Total_Spending", "sum")
    ).reset_index()

    fig = go.Figure(go.Pie(
        labels=type_data["Customer_Type"],
        values=type_data["Spending"],
        hole=0.56,
        marker=dict(colors=["#722F45", "#D69A42"]),
        textinfo="percent",
        textposition="inside",
        insidetextfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(fig, "Revenue: New vs Returning Customers", height=430, legend_position="bottom")
    return fig

def chart_top_10_customers_spend(cust_df: pd.DataFrame) -> go.Figure:
    """Top 10 Customers by Total Spending."""
    if cust_df.empty or "Total_Spending" not in cust_df.columns:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Top 10 Customers", height=420)

    top10 = cust_df.sort_values("Total_Spending", ascending=True).tail(10)

    fig = go.Figure(go.Bar(
        x=top10["Total_Spending"],
        y=top10["Customer_Name"],
        orientation="h",
        marker_color="#4A1F2D",
        text=top10["Total_Spending"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Lifetime Spend: $%{x:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Top 10 VIP Clients (Lifetime Value)", height=420, show_legend=False)
    fig.update_layout(xaxis_title="Lifetime Spend ($)", yaxis_title="")
    return fig
