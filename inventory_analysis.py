"""
Inventory Analytics Module
Monitors stock levels, valuations, inventory health, and generates data-driven reorder recommendations.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from chart_theme import apply_luxury_theme, LUXURY_PALETTE, BURGUNDY_MONOCHROME

def compute_inventory_health(
    products_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    overstock_threshold: int = 100,
    lead_time_days: int = 14,
    safety_stock_days: int = 7
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes stock status, inventory valuation, run rate, and recommended purchase quantities.
    """
    inv_df = products_df.copy()

    # Calculate historical units sold from sales_df
    if not sales_df.empty and "Product_ID" in sales_df.columns:
        sold_summary = sales_df.groupby("Product_ID").agg(
            Units_Sold=("Quantity", "sum")
        ).reset_index()
        inv_df = inv_df.merge(sold_summary, on="Product_ID", how="left")
        inv_df["Units_Sold"] = inv_df["Units_Sold"].fillna(0).astype(int)

        # Calculate daily sales run-rate over the dataset period
        min_date = pd.to_datetime(sales_df["Order_Date"]).min()
        max_date = pd.to_datetime(sales_df["Order_Date"]).max()
        days_span = max(1, (max_date - min_date).days + 1)
        inv_df["Daily_Run_Rate"] = (inv_df["Units_Sold"] / days_span).round(3)
    else:
        inv_df["Units_Sold"] = 0
        inv_df["Daily_Run_Rate"] = 0.0

    # Ensure required columns
    if "Reorder_Level" not in inv_df.columns:
        inv_df["Reorder_Level"] = 15
    if "Cost_Price" not in inv_df.columns:
        inv_df["Cost_Price"] = inv_df["Selling_Price"] * 0.45

    inv_df["Available_Stock"] = inv_df["Available_Stock"].fillna(0).astype(int)
    inv_df["Inventory_Value"] = (inv_df["Available_Stock"] * inv_df["Selling_Price"]).round(2)
    inv_df["Cost_Inventory_Value"] = (inv_df["Available_Stock"] * inv_df["Cost_Price"]).round(2)

    # Classify Stock Status
    def determine_status(row):
        stock = row["Available_Stock"]
        reorder = row["Reorder_Level"]
        if stock == 0:
            return "Out of Stock"
        elif stock <= reorder:
            return "Low Stock"
        elif stock >= overstock_threshold:
            return "Overstocked"
        else:
            return "In Stock"

    inv_df["Stock_Status"] = inv_df.apply(determine_status, axis=1)

    # Reorder Suggestion Formula:
    # Target Inventory = (Lead Time Days + Safety Stock Days) * Daily Velocity
    # Suggested Reorder Qty = Target Inventory - Current Available Stock
    def calculate_reorder_qty(row):
        velocity = row["Daily_Run_Rate"]
        stock = row["Available_Stock"]
        reorder_point = row["Reorder_Level"]
        
        target_buffer = int(np.ceil((lead_time_days + safety_stock_days) * velocity))
        target_buffer = max(target_buffer, reorder_point * 2)
        
        needed = target_buffer - stock
        if stock <= reorder_point:
            return max(0, needed)
        elif stock == 0:
            return max(target_buffer, reorder_point * 2)
        return 0

    inv_df["Suggested_Reorder_Qty"] = inv_df.apply(calculate_reorder_qty, axis=1)

    # Days of Inventory Remaining (DOIR)
    def calculate_doir(row):
        rate = row["Daily_Run_Rate"]
        stock = row["Available_Stock"]
        if rate <= 0:
            return 999.0
        return round(stock / rate, 1)

    inv_df["Days_Inventory_Remaining"] = inv_df.apply(calculate_doir, axis=1)

    # High-level KPIs
    total_stock = int(inv_df["Available_Stock"].sum())
    total_inv_value = float(inv_df["Inventory_Value"].sum())
    low_stock_count = int((inv_df["Stock_Status"] == "Low Stock").sum())
    out_of_stock_count = int((inv_df["Stock_Status"] == "Out of Stock").sum())
    overstocked_count = int((inv_df["Stock_Status"] == "Overstocked").sum())

    kpis = {
        "total_stock": total_stock,
        "inventory_value": total_inv_value,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "overstocked_count": overstocked_count,
        "total_products": len(inv_df),
        "lead_time_days": lead_time_days,
        "safety_stock_days": safety_stock_days
    }

    return inv_df, kpis

def chart_stock_by_category(inv_df: pd.DataFrame) -> go.Figure:
    """Stock by Category bar chart."""
    if inv_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Stock by Category")

    cat_stock = inv_df.groupby("Category")["Available_Stock"].sum().reset_index()
    cat_stock = cat_stock.sort_values("Available_Stock", ascending=False)

    fig = go.Figure(go.Bar(
        x=cat_stock["Category"],
        y=cat_stock["Available_Stock"],
        marker_color="#722F45",
        text=cat_stock["Available_Stock"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Available Stock: %{y} units<extra></extra>"
    ))

    apply_luxury_theme(fig, "Available Inventory Units by Category", height=420, show_legend=False)
    fig.update_layout(xaxis_title="", yaxis_title="Units in Stock")
    return fig

def chart_low_stock_products(inv_df: pd.DataFrame) -> go.Figure:
    """Grouped horizontal bar chart for critical stock replenishment."""
    if inv_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Critical Replenishment Alerts", height=430)

    critical = inv_df[inv_df["Stock_Status"].isin(["Low Stock", "Out of Stock"])].copy()
    critical = critical.sort_values("Available_Stock", ascending=True)

    if critical.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="All catalog styles have healthy inventory levels.",
            showarrow=False,
            font=dict(size=14, color="#43866B")
        )
        return apply_luxury_theme(fig, "Stock Replenishment Status", height=430)

    fig = go.Figure()

    # Bar 1: Available Physical Stock
    fig.add_trace(go.Bar(
        y=critical["Product_Name"],
        x=critical["Available_Stock"],
        name="Available Physical Stock",
        orientation="h",
        marker=dict(
            color=critical["Stock_Status"].apply(lambda s: "#C75C5C" if s == "Out of Stock" else "#D69A42"),
            line=dict(color="#FFFDF9", width=1)
        ),
        text=critical["Available_Stock"].apply(lambda s: f"{s} units (Out)" if s == 0 else f"{s} units"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Available Physical Stock: %{x} units<extra></extra>"
    ))

    # Bar 2: Safety Reorder Level Target
    fig.add_trace(go.Bar(
        y=critical["Product_Name"],
        x=critical["Reorder_Level"],
        name="Safety Reorder Threshold",
        orientation="h",
        marker=dict(
            color="#4A1F2D",
            line=dict(color="#FFFDF9", width=1)
        ),
        text=critical["Reorder_Level"].apply(lambda r: f"Target: {r}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Safety Reorder Threshold: %{x} units<extra></extra>"
    ))

    chart_height = max(440, len(critical) * 55)
    apply_luxury_theme(
        fig,
        "Urgent Replenishment Alerts: Stock vs. Reorder Threshold",
        height=chart_height,
        barmode="group",
        legend_position="bottom",
        custom_margin=dict(l=220, r=60, t=65, b=75)
    )
    fig.update_layout(xaxis_title="Stock Quantity (Units)", yaxis_title="")
    return fig

def chart_inventory_distribution(inv_df: pd.DataFrame) -> go.Figure:
    """Inventory Health Distribution Donut."""
    if inv_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Inventory Health Distribution", height=430)

    stat_data = inv_df["Stock_Status"].value_counts().reset_index()
    stat_data.columns = ["Status", "Count"]

    color_map = {
        "In Stock": "#43866B",
        "Low Stock": "#D69A42",
        "Out of Stock": "#C75C5C",
        "Overstocked": "#4A1F2D"
    }
    colors = [color_map.get(s, "#887F78") for s in stat_data["Status"]]

    fig = go.Figure(go.Pie(
        labels=stat_data["Status"],
        values=stat_data["Count"],
        hole=0.58,
        marker=dict(colors=colors),
        textinfo="percent",
        textposition="inside",
        insidetextfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>SKUs: %{value}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='horizontal')

    apply_luxury_theme(
        fig,
        "Inventory Health Distribution",
        height=430,
        legend_position="bottom",
        custom_margin=dict(l=35, r=35, t=65, b=80)
    )
    return fig

def chart_sales_vs_stock_scatter(inv_df: pd.DataFrame) -> go.Figure:
    """Best-Selling Products vs Remaining Stock Scatter Plot (Executive 4-Quadrant Matrix)."""
    if inv_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Sales Velocity vs Stock Matrix", height=520)

    status_colors = {
        "Out of Stock": "#C75C5C",
        "Low Stock": "#D69A42",
        "In Stock": "#43866B",
        "Overstocked": "#4A1F2D"
    }

    fig = go.Figure()

    # Separate traces per Stock Status for interactive filtering in legend
    for status, color in status_colors.items():
        subset = inv_df[inv_df["Stock_Status"] == status]
        if subset.empty:
            continue

        fig.add_trace(go.Scatter(
            x=subset["Units_Sold"],
            y=subset["Available_Stock"],
            mode="markers",
            name=status,
            marker=dict(
                size=np.clip(subset["Selling_Price"] / 8 + 10, 12, 28),
                color=color,
                opacity=0.88,
                line=dict(color="#FFFDF9", width=1.5)
            ),
            customdata=np.stack((
                subset["Product_Name"],
                subset["Category"],
                subset["Selling_Price"],
                subset["Stock_Status"],
                subset["Daily_Run_Rate"]
            ), axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Category: %{customdata[1]}<br>"
                "Status: %{customdata[3]}<br>"
                "Available Stock: <b>%{y:,} units</b><br>"
                "Historical Velocity: <b>%{x:,} units sold</b> (%{customdata[4]} /day)<br>"
                "Price: $%{customdata[2]:,.2f}<extra></extra>"
            )
        ))

    # Add subtle non-overlapping annotations for key strategic outliers
    top_seller = inv_df.sort_values("Units_Sold", ascending=False).iloc[0]
    fig.add_annotation(
        x=top_seller["Units_Sold"],
        y=top_seller["Available_Stock"],
        text=f"★ Top Seller: {top_seller['Product_Name'][:18]}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="#4A1F2D",
        ax=40,
        ay=-30,
        font=dict(family="Plus Jakarta Sans", size=10, color="#4A1F2D"),
        bgcolor="rgba(255, 253, 249, 0.9)",
        bordercolor="#4A1F2D",
        borderwidth=1,
        borderpad=3
    )

    stockouts = inv_df[inv_df["Stock_Status"] == "Out of Stock"]
    if not stockouts.empty:
        critical_out = stockouts.sort_values("Units_Sold", ascending=False).iloc[0]
        fig.add_annotation(
            x=critical_out["Units_Sold"],
            y=critical_out["Available_Stock"],
            text=f"⚠ Out of Stock: {critical_out['Product_Name'][:18]}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor="#C75C5C",
            ax=-40,
            ay=-35,
            font=dict(family="Plus Jakarta Sans", size=10, color="#C75C5C"),
            bgcolor="rgba(255, 253, 249, 0.9)",
            bordercolor="#C75C5C",
            borderwidth=1,
            borderpad=3
        )

    # Reference lines for 4-quadrant strategic decision making
    med_sales = inv_df["Units_Sold"].median()
    reorder_ref = inv_df["Reorder_Level"].median()

    fig.add_hline(
        y=reorder_ref,
        line_dash="dot",
        line_color="rgba(199, 92, 92, 0.5)",
        annotation_text="Safety Reorder Threshold",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#C75C5C")
    )
    fig.add_vline(
        x=med_sales,
        line_dash="dot",
        line_color="rgba(136, 127, 120, 0.5)",
        annotation_text="Median Sales Velocity",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#887F78")
    )

    apply_luxury_theme(
        fig,
        "Strategic Merchandising Matrix: Sales Velocity vs. Remaining Stock",
        height=520,
        legend_position="bottom",
        custom_margin=dict(l=65, r=40, t=65, b=75)
    )
    fig.update_layout(
        xaxis_title="Historical Sales Volume (Units Sold)",
        yaxis_title="Available Physical Stock (Units)"
    )
    return fig

def chart_category_inventory_value(inv_df: pd.DataFrame) -> go.Figure:
    """Category-wise Inventory Value Bar Chart."""
    if inv_df.empty:
        fig = go.Figure()
        return apply_luxury_theme(fig, "Category Inventory Value", height=420)

    val_data = inv_df.groupby("Category")["Inventory_Value"].sum().reset_index()
    val_data = val_data.sort_values("Inventory_Value", ascending=False)

    fig = go.Figure(go.Bar(
        x=val_data["Category"],
        y=val_data["Inventory_Value"],
        marker_color="#D69A42",
        text=val_data["Inventory_Value"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Holding Capital: $%{y:,.2f}<extra></extra>"
    ))

    apply_luxury_theme(fig, "Holding Inventory Value by Category (Retail)", height=420, show_legend=False)
    fig.update_layout(xaxis_title="", yaxis_title="Inventory Value ($)")
    return fig
