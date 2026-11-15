"""
Export & Reporting Module
Generates high-fidelity CSV, multi-sheet formatted Excel (.xlsx), and executive PDF summary dossiers.
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable

def generate_csv_bytes(df: pd.DataFrame) -> bytes:
    """Encodes a DataFrame into UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")

def generate_excel_analytics_report(
    sales_df: pd.DataFrame,
    product_perf_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    recommendations: Dict[str, List[Dict[str, str]]],
    brand_name: str = "Atelier Royale",
    date_filter_str: str = "All Time"
) -> bytes:
    """
    Constructs an editorial-grade multi-tab Excel workbook with styled headers, borders, and number formats.
    """
    output = io.BytesIO()
    wb = openpyxl.Workbook()
    
    # Header styles
    burgundy_fill = PatternFill(start_color="722F45", end_color="722F45", fill_type="solid")
    gold_fill = PatternFill(start_color="D69A42", end_color="D69A42", fill_type="solid")
    light_cream_fill = PatternFill(start_color="F8F5F0", end_color="F8F5F0", fill_type="solid")
    
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="4A1F2D")
    meta_font = Font(name="Calibri", size=10, italic=True, color="887F78")
    data_font = Font(name="Calibri", size=10, color="292321")
    
    thin_border_side = Side(border_style="thin", color="E0D9D0")
    data_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    # -------------------------------------------------------------
    # TAB 1: EXECUTIVE OVERVIEW
    # -------------------------------------------------------------
    ws_exec = wb.active
    ws_exec.title = "Executive_Summary"
    ws_exec.views.sheetView[0].showGridLines = True
    
    ws_exec["A1"] = f"{brand_name.upper()} - FASHION BUSINESS INTELLIGENCE"
    ws_exec["A1"].font = title_font
    ws_exec["A2"] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Active Date Filter: {date_filter_str}"
    ws_exec["A2"].font = meta_font
    
    total_rev = sales_df["Total_Amount"].sum() if not sales_df.empty else 0.0
    total_orders = sales_df["Order_ID"].nunique() if not sales_df.empty else 0
    total_units = sales_df["Quantity"].sum() if not sales_df.empty else 0
    aov = total_rev / total_orders if total_orders > 0 else 0.0
    
    kpis = [
        ("Metric", "Value", "Notes"),
        ("Total Gross Revenue", f"${total_rev:,.2f}", "Calculated from filtered transactions"),
        ("Total Order Transactions", f"{total_orders:,}", "Distinct order IDs"),
        ("Total Apparel Units Sold", f"{total_units:,}", "Volume shipped across all SKUs"),
        ("Average Order Value (AOV)", f"${aov:,.2f}", "Revenue per completed transaction"),
        ("Total Customers Active", f"{customer_df['Customer_ID'].nunique():,}", "Unique registered accounts"),
        ("Catalog Active SKUs", f"{len(product_perf_df):,}", "Active styles in brand catalog"),
        ("Total Inventory Stock on Hand", f"{inventory_df['Available_Stock'].sum():,} units", "Current warehouse physical count"),
        ("Total Inventory Holding Value", f"${inventory_df['Inventory_Value'].sum():,.2f}", "Retail valuation of current stock"),
    ]
    
    for r_idx, row in enumerate(kpis, start=5):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_exec.cell(row=r_idx, column=c_idx, value=val)
            if r_idx == 5:
                cell.fill = burgundy_fill
                cell.font = header_font
            else:
                cell.font = data_font
                cell.border = data_border
                if c_idx == 1:
                    cell.font = Font(name="Calibri", size=10, bold=True, color="4A1F2D")
                    cell.fill = light_cream_fill

    # -------------------------------------------------------------
    # HELPER: POPULATE DATA TABS
    # -------------------------------------------------------------
    def populate_data_sheet(ws, title, df, date_cols=[]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = f"{brand_name} | {title}"
        ws["A1"].font = Font(name="Calibri", size=13, bold=True, color="4A1F2D")
        
        # Headers
        headers = list(df.columns)
        for c_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=c_idx, value=h.replace("_", " "))
            cell.fill = burgundy_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        # Rows
        for r_idx, row_vals in enumerate(df.values, start=4):
            for c_idx, val in enumerate(row_vals, start=1):
                col_name = headers[c_idx - 1]
                # Format dates to string
                if isinstance(val, (pd.Timestamp, datetime)):
                    val = val.strftime("%Y-%m-%d")
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.font = data_font
                cell.border = data_border
                
                # Alignments and number formats
                if isinstance(val, (int, float)):
                    if any(term in col_name.lower() for term in ["price", "amount", "revenue", "spending", "value"]):
                        cell.number_format = '$#,##0.00'
                    elif any(term in col_name.lower() for term in ["qty", "units", "quantity", "stock", "orders", "age"]):
                        cell.number_format = '#,##0'

    # TAB 2: Sales Transactions
    ws_sales = wb.create_sheet(title="Sales_Data")
    # Clean export columns
    export_sales = sales_df.copy()
    if "Order_Date" in export_sales.columns:
        export_sales["Order_Date"] = export_sales["Order_Date"].astype(str)
    keep_sales_cols = [c for c in export_sales.columns if c not in ["Month_Year", "Month_Name", "Day_Name", "Year"]]
    populate_data_sheet(ws_sales, "Filtered Sales Transactions", export_sales[keep_sales_cols])

    # TAB 3: Product Performance
    ws_prod = wb.create_sheet(title="Product_Performance")
    populate_data_sheet(ws_prod, "Product Performance & Quantile Status", product_perf_df)

    # TAB 4: Customer Analytics
    ws_cust = wb.create_sheet(title="Customer_Analytics")
    cust_export = customer_df.copy()
    for d_col in ["First_Order", "Last_Order", "Registration_Date"]:
        if d_col in cust_export.columns:
            cust_export[d_col] = cust_export[d_col].astype(str)
    populate_data_sheet(ws_cust, "Customer Lifetime Profiles & Segments", cust_export)

    # TAB 5: Inventory & Reorders
    ws_inv = wb.create_sheet(title="Inventory_Reorders")
    populate_data_sheet(ws_inv, "Inventory Health & Suggested Replenishment", inventory_df)

    # TAB 6: Strategic Recommendations
    ws_rec = wb.create_sheet(title="Strategic_Recommendations")
    ws_rec.views.sheetView[0].showGridLines = True
    ws_rec["A1"] = f"{brand_name} | AI & Data-Driven Strategic Actions"
    ws_rec["A1"].font = Font(name="Calibri", size=13, bold=True, color="4A1F2D")

    rec_rows = []
    for item in recommendations.get("positive_insights", []):
        rec_rows.append(("Positive Insight", item.get("title", ""), item.get("metric", ""), item.get("description", "")))
    for item in recommendations.get("attention_areas", []):
        rec_rows.append(("Area for Attention", item.get("title", ""), item.get("metric", ""), item.get("description", "")))
    for item in recommendations.get("recommended_actions", []):
        rec_rows.append(("Action Recommendation", item.get("title", ""), item.get("impact", ""), item.get("action", "")))

    rec_df = pd.DataFrame(rec_rows, columns=["Category", "Topic", "Metric / Impact", "Actionable Guidance"])
    populate_data_sheet(ws_rec, "Strategic Insights & Business Recommendations", rec_df)

    # Auto-adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(42, max(max_len + 3, 12))

    wb.save(output)
    output.seek(0)
    return output.getvalue()

def generate_pdf_summary_report(
    kpi_dict: Dict[str, Any],
    top_products_df: pd.DataFrame,
    recommendations: Dict[str, List[Dict[str, str]]],
    brand_name: str = "Atelier Royale",
    date_filter_str: str = "Last 30 Days",
    student_info: Optional[Dict[str, str]] = None
) -> bytes:
    """
    Compiles an executive summary PDF dossier using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom luxury PDF typography styles
    burgundy_color = colors.HexColor("#722F45")
    dark_burgundy = colors.HexColor("#4A1F2D")
    gold_color = colors.HexColor("#D69A42")
    cream_bg = colors.HexColor("#F8F5F0")
    charcoal_text = colors.HexColor("#292321")
    muted_grey = colors.HexColor("#887F78")

    title_style = ParagraphStyle(
        "LuxuryTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=dark_burgundy,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        "LuxurySubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=muted_grey,
        spaceAfter=12
    )
    
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=burgundy_color,
        spaceBefore=14,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=charcoal_text
    )

    bold_cell_style = ParagraphStyle(
        "BoldCell",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=dark_burgundy
    )

    story = []

    # 1. HEADER & BRAND BANNER
    story.append(Paragraph(f"<b>{brand_name.upper()} &bull; FASHION BRAND ANALYTICS</b>", title_style))
    story.append(Paragraph(f"Executive Business Performance Dossier &bull; Date Range: <b>{date_filter_str}</b> &bull; Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=burgundy_color, spaceBefore=2, spaceAfter=12))

    # 2. ACADEMIC SUBMISSION DETAILS (If provided)
    if student_info:
        student_data = [
            [
                Paragraph(f"<b>Student Name:</b> {student_info.get('name', 'N/A')}", body_style),
                Paragraph(f"<b>Department:</b> {student_info.get('department', 'N/A')}", body_style)
            ],
            [
                Paragraph(f"<b>Course / Class:</b> {student_info.get('class', 'N/A')}", body_style),
                Paragraph(f"<b>Institution:</b> {student_info.get('college', 'N/A')}", body_style)
            ]
        ]
        student_table = Table(student_data, colWidths=[270, 270])
        student_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDF9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE9DF")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(student_table)
        story.append(Spacer(1, 10))

    # 3. EXECUTIVE KPI METRICS MATRIX
    story.append(Paragraph("1. Executive Performance Metrics", section_heading))
    kpi_table_data = [
        [
            Paragraph("<b>Total Revenue</b>", bold_cell_style),
            Paragraph(f"${kpi_dict.get('total_revenue', 0.0):,.2f}", bold_cell_style),
            Paragraph("<b>Total Orders</b>", bold_cell_style),
            Paragraph(f"{kpi_dict.get('total_orders', 0):,}", body_style)
        ],
        [
            Paragraph("<b>Average Order Value</b>", bold_cell_style),
            Paragraph(f"${kpi_dict.get('aov', 0.0):,.2f}", body_style),
            Paragraph("<b>Total Units Sold</b>", bold_cell_style),
            Paragraph(f"{kpi_dict.get('total_units', 0):,}", body_style)
        ],
        [
            Paragraph("<b>Active Customers</b>", bold_cell_style),
            Paragraph(f"{kpi_dict.get('total_customers', 0):,}", body_style),
            Paragraph("<b>Avg Daily Revenue</b>", bold_cell_style),
            Paragraph(f"${kpi_dict.get('avg_daily_revenue', 0.0):,.2f}", body_style)
        ]
    ]
    kpi_table = Table(kpi_table_data, colWidths=[140, 130, 140, 130])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDF9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE9DF")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    # 4. TOP PERFORMING HERO PRODUCTS
    story.append(Paragraph("2. Top Revenue Hero Products", section_heading))
    if not top_products_df.empty:
        prod_headers = [
            Paragraph("<b>Product Name</b>", bold_cell_style),
            Paragraph("<b>Category</b>", bold_cell_style),
            Paragraph("<b>Price</b>", bold_cell_style),
            Paragraph("<b>Units Sold</b>", bold_cell_style),
            Paragraph("<b>Revenue</b>", bold_cell_style),
            Paragraph("<b>Status</b>", bold_cell_style)
        ]
        prod_rows = [prod_headers]
        for _, row in top_products_df.head(5).iterrows():
            prod_rows.append([
                Paragraph(str(row["Product_Name"]), body_style),
                Paragraph(str(row.get("Category", "N/A")), body_style),
                Paragraph(f"${row.get('Selling_Price', 0):,.2f}", body_style),
                Paragraph(str(int(row.get("Units_Sold", 0))), body_style),
                Paragraph(f"${row.get('Revenue', 0):,.2f}", bold_cell_style),
                Paragraph(str(row.get("Performance_Status", "N/A")), body_style)
            ])
        p_table = Table(prod_rows, colWidths=[160, 95, 65, 65, 85, 70])
        p_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), burgundy_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE9DF")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(p_table)
    else:
        story.append(Paragraph("No product performance data available for this filter.", body_style))
    story.append(Spacer(1, 10))

    # 5. STRATEGIC POSITIVE FINDINGS & RECOMMENDATIONS
    story.append(Paragraph("3. AI Business Insights & Recommended Actions", section_heading))
    
    # Positive Insights
    for p_item in recommendations.get("positive_insights", [])[:2]:
        p_text = f"<b>&bull; [POSITIVE] {p_item.get('title', '')}</b> ({p_item.get('metric', '')}): {p_item.get('description', '')}"
        story.append(Paragraph(p_text, body_style))
        story.append(Spacer(1, 4))

    # Areas of Attention
    for a_item in recommendations.get("attention_areas", [])[:2]:
        a_text = f"<b>&bull; [ATTENTION REQUIRED] {a_item.get('title', '')}</b> ({a_item.get('metric', '')}): {a_item.get('description', '')}"
        story.append(Paragraph(a_text, body_style))
        story.append(Spacer(1, 4))

    # Strategic Actions
    for r_item in recommendations.get("recommended_actions", [])[:3]:
        r_text = f"<b>&bull; [RECOMMENDED ACTION] {r_item.get('title', '')}</b> (Priority: {r_item.get('urgency', 'High')}): {r_item.get('action', '')} <i>Impact: {r_item.get('impact', '')}</i>"
        story.append(Paragraph(r_text, body_style))
        story.append(Spacer(1, 4))

    # 6. SIGN-OFF BLOCK
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D9D2C7"), spaceBefore=4, spaceAfter=8))
    sign_data = [
        [
            Paragraph("<b>Evaluator Signature:</b> ___________________________", body_style),
            Paragraph("<b>Date of Review:</b> ___________________________", body_style)
        ]
    ]
    sign_table = Table(sign_data, colWidths=[270, 270])
    story.append(sign_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
