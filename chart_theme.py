"""
Plotly Theme & Chart Styling Helper
Provides consistent, editorial luxury fashion styling for Plotly charts with robust spacing and collision prevention.
"""

from typing import Optional, Dict
import plotly.graph_objects as go

LUXURY_PALETTE = [
    "#722F45",  # Primary Burgundy
    "#D69A42",  # Warm Gold
    "#43866B",  # Sage Emerald
    "#4A1F2D",  # Deep Burgundy
    "#887F78",  # Editorial Warm Grey
    "#C75C5C",  # Coral Berry
    "#A3485E",  # Rose Burgundy
    "#365563",  # Deep Slate
]

BURGUNDY_MONOCHROME = [
    "#EEDDE2",
    "#D8B3C1",
    "#BA7A92",
    "#8E3E58",
    "#722F45",
    "#4A1F2D"
]

def apply_luxury_theme(
    fig: go.Figure,
    title: str = "",
    height: int = 430,
    show_legend: bool = True,
    barmode: str = "relative",
    legend_position: str = "bottom",
    custom_margin: Optional[Dict[str, int]] = None
) -> go.Figure:
    """
    Applies luxury editorial styling with guaranteed spacing between title, legend, and chart elements.
    """
    # Generous margins to guarantee zero clipping or collision
    if custom_margin:
        margin = custom_margin
    elif legend_position == "bottom" and show_legend:
        margin = dict(l=50, r=35, t=65 if title else 25, b=80)
    elif legend_position == "right" and show_legend:
        margin = dict(l=50, r=130, t=65 if title else 25, b=45)
    elif legend_position == "top_right" and show_legend:
        margin = dict(l=50, r=35, t=85 if title else 35, b=45)
    else:
        margin = dict(l=50, r=35, t=65 if title else 25, b=45)

    # Clean bottom horizontal legend
    if legend_position == "bottom":
        legend_config = dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(family="Plus Jakarta Sans", size=11, color="#887F78")
        )
    elif legend_position == "right":
        legend_config = dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(family="Plus Jakarta Sans", size=11, color="#887F78")
        )
    else:  # top_right
        legend_config = dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1.0,
            font=dict(family="Plus Jakarta Sans", size=11, color="#887F78")
        )

    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "font": {"family": "Cormorant Garamond, Georgia, serif", "size": 18, "color": "#4A1F2D"},
            "x": 0.02,
            "y": 0.98,
            "xanchor": "left",
            "yanchor": "top",
            "pad": dict(b=12)
        },
        paper_bgcolor="rgba(255, 253, 249, 0)",
        plot_bgcolor="rgba(255, 253, 249, 0)",
        font={"family": "Plus Jakarta Sans, sans-serif", "size": 12, "color": "#292321"},
        margin=margin,
        height=height,
        autosize=True,
        showlegend=show_legend,
        barmode=barmode,
        legend=legend_config if show_legend else None,
        hoverlabel=dict(
            bgcolor="#FFFDF9",
            bordercolor="#722F45",
            font=dict(family="Plus Jakarta Sans", size=12, color="#292321")
        )
    )
    
    # Clean subtle axis grids
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EFE9DF",
        gridwidth=1,
        zeroline=False,
        linecolor="#D9D2C7",
        tickfont=dict(color="#887F78", size=11)
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EFE9DF",
        gridwidth=1,
        zeroline=False,
        linecolor="#D9D2C7",
        tickfont=dict(color="#887F78", size=11)
    )
    
    return fig
