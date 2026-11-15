# 👑 Fashion Brand Analytics — Business Intelligence & Decision Support System

> **An End-to-End Academic AI & Data Science Project for Luxury and Contemporary Fashion Retailers**

---

## 📖 1. Project Overview

**Fashion Brand Analytics** is a complete, professional, interactive data analytics web application developed in Python and Streamlit. Designed specifically for fashion retail executives and merchandisers, the platform bridges the gap between raw, transactional retail data and high-impact strategic decisions.

### Core Value Proposition:
- **Sales Intelligence:** Uncover revenue drivers, seasonality, ticket size trends, and geographic strongholds.
- **Product Merchandising:** Automatically classify catalog items into **Best Sellers**, **Average Performers**, and **Underperformers** using statistical quartiles.
- **Customer Lifetime Value (LTV):** Segment clientele into **VIP / High-Value**, **Regular**, **Occasional**, and **Low-Value** cohorts using purchase frequency and spending.
- **Inventory & Replenishment:** Monitor physical stock vs. safety reorder thresholds, calculate Days of Inventory Remaining (DOIR), and dynamically recommend purchase order quantities.
- **Algorithmic Business Recommendations:** Generate genuinely data-grounded strategic guidance categorized into **Positive Insights**, **Risk Areas**, and **Recommended Actions**.
- **Data Governance:** Upload custom CSV/Excel files, auto-map columns, run data health diagnostics, perform safe data cleaning, and export reports in CSV, formatted multi-tab Excel (`.xlsx`), and PDF.

---

## 🏗️ 2. Project Architecture & Folder Structure

```
fashion_brand_analytics/
│
├── app.py                      # Main Streamlit application and page router
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete academic documentation & presentation guide
│
├── data/
│   ├── generate_data.py        # Synthetic fashion data generator (Pareto & realistic curves)
│   └── sample_data/            # Pre-generated consistent demo datasets
│       ├── sales.csv           # 1,250 sales transactions
│       ├── products.csv        # 36 luxury & contemporary products
│       ├── customers.csv       # 120 customer profiles
│       └── fashion_brand_demo.xlsx # Multi-tab demonstration workbook
│
├── modules/
│   ├── __init__.py             # Module initialization
│   ├── chart_theme.py          # Bespoke luxury editorial Plotly color palette & styling
│   ├── data_loader.py          # Data ingestion, relational joins, fuzzy column mapping
│   ├── data_cleaning.py        # Quality health audit, anomaly detection, safe cleaning
│   ├── sales_analysis.py       # Sales KPIs, trends, categorical and geographic breakdowns
│   ├── product_analysis.py     # Product velocity, quartile classification, size/color mix
│   ├── customer_analysis.py    # Demographic distributions, cohort LTV, VIP segmentation
│   ├── inventory_analysis.py   # Stockout mitigation, DOIR calculation, reorder engine
│   ├── recommendations.py      # Multi-factor algorithmic business recommendation rules
│   └── export_reports.py       # Multi-sheet styled Excel (.xlsx) and ReportLab PDF generator
│
└── assets/
    └── styles.css              # Custom editorial luxury CSS design system
```

---

## 🎨 3. Luxury Editorial Design System

The application intentionally avoids default Streamlit aesthetics, employing an editorial luxury fashion design language:
- **Background:** `#F8F5F0` (Warm Cream Editorial Tone)
- **Primary Burgundy:** `#722F45` (Royal Burgundy Accent)
- **Deep Burgundy:** `#4A1F2D` (Header & Sidebar Base)
- **Cream Surface:** `#FFFDF9` (Clean Card Surface with Subtle Drop Shadow)
- **Gold Accent:** `#D69A42` (Key Metric & Highlight Accent)
- **Forest Sage:** `#43866B` (Positive Insights & Stock Healthy)
- **Coral Berry:** `#C75C5C` (Risk Indicators & Stockout Alerts)
- **Typography:** *Cormorant Garamond* serif headings paired with clean *Plus Jakarta Sans* UI metrics.

---

## 🚀 4. Installation & Quick Start Guide

### Prerequisites
- Python 3.9 to 3.13 installed on your machine.
- Web browser (Chrome, Edge, Firefox, or Safari).

### Step 1: Navigate to Project Directory
```powershell
cd fashion_brand_analytics
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Application
```powershell
streamlit run app.py
```

The application will launch automatically in your default browser at `http://localhost:8501`.

---

## 📊 5. Modules & Analytical Methodologies

### Module 1: Dashboard Overview
- **Executive KPIs:** Total Revenue, Total Orders, Units Sold, Average Order Value (AOV), Active Customers, Active Products.
- **Dynamic Filters:** Date presets (`All Time`, `Today`, `Last 7/30/90 Days`, `This Year`, `Custom Range`), Category, Brand, and Region filters.
- **Visuals:** Spline-interpolated revenue line with shaded gradient, categorical donut share, top 5 bestsellers, regional bar charts, recent transactions register.

### Module 2: Sales Analytics
- **Trends:** Daily revenue with 7-day rolling moving average, monthly MoM volume comparisons.
- **Breakdowns:** Payment gateway mix (Credit Card, UPI, Debit Card, Net Banking, COD) and territory revenue.
- **Searchable Ledger:** Filter transactions by Order ID, Customer Name, or Product.

### Module 3: Product Analytics & Quantile Classification
- **Classification Formula:**
  $$\text{Best Seller} = \text{Revenue} \ge Q_{75}(\text{Revenue}) \lor \text{Units} \ge Q_{75}(\text{Units})$$
  $$\text{Underperformer} = \text{Revenue} \le Q_{25}(\text{Revenue}) \land \text{Units} \le Q_{25}(\text{Units})$$
  $$\text{Average Performer} = \text{Otherwise}$$
- **Visuals:** Top 10 Revenue Generators vs. Bottom 10 Underperformers, Size-run velocity (XS through Free Size), Colorway sales distribution.

### Module 4: Customer Analytics & Behavioral Segmentation
- **Segmentation Model:**
  - **High-Value (VIP):** Orders $\ge 2$ and Spend $\ge Q_{75}(\text{Spend})$.
  - **Regular:** Orders $\ge 2$ and $Q_{25}(\text{Spend}) \le \text{Spend} < Q_{75}(\text{Spend})$.
  - **Occasional:** Single purchase with Spend $\ge \text{Median}$.
  - **Low-Value:** Single purchase with below-median spend.
- **Visuals:** Age demographic histogram, Gender distribution, Segment revenue contribution, Top 10 VIP patrons.

### Module 5: Inventory Analytics & Replenishment Modeling
- **Stock Status Engine:**
  - `Out of Stock`: Stock $= 0$
  - `Low Stock`: $0 < \text{Stock} \le \text{Reorder Level}$
  - `In Stock`: $\text{Reorder Level} < \text{Stock} \le \text{Overstock Threshold}$
  - `Overstocked`: $\text{Stock} > \text{Overstock Threshold}$
- **Dynamic Reorder Calculation:**
  $$\text{Daily Run Rate} = \frac{\text{Total Units Sold}}{\text{Days Span}}$$
  $$\text{DOIR (Days of Inventory Remaining)} = \frac{\text{Available Stock}}{\text{Daily Run Rate}}$$
  $$\text{Target Buffer} = (\text{Supplier Lead Time} + \text{Safety Buffer}) \times \text{Daily Run Rate}$$
  $$\text{Suggested Reorder Qty} = \max(0, \text{Target Buffer} - \text{Available Stock})$$

### Module 6: Business Recommendations Engine
- Algorithmic evaluation of live metrics:
  - **Hero SKU Stockout Vulnerability:** Identifies products with high sales velocity near depletion and generates urgent PO advisories.
  - **Deadstock Capital Lockup:** Identifies overstocked slow-moving lines and recommends promotional bundle strategies.
  - **Retention & LTV Programs:** Evaluates repeat buyer revenue share to recommend VIP loyalty programs.
  - **Regional Expansion:** Detects high-performing vs under-indexed territories.

### Module 7: Data Management & Quality Control
- **File Ingestion:** Drag-and-drop CSV or Excel (`.xlsx`, `.xls`) upload.
- **Fuzzy Column Mapper:** Automatically handles synonyms (`Order Date`, `order_date`, `invoice_date` $\rightarrow$ `Order_Date`).
- **Hygiene Profiler:** Detects missing value rates, duplicate rows, negative currency amounts, unparseable dates, and outputs an overall **Data Health Score (0-100)**.
- **Safe Cleaner:** Non-destructive median/mode imputation, deduplication, and anomaly correction with an audit changelog.

### Module 8: About Project & Academic Presentation
- Complete system architecture flowchart.
- Editable Student Submission Section (Student Name, Class, Department, College Name) persisted in session state and automatically embedded in exported PDF dossiers.

---

## 📑 6. Export Options
1. **CSV Reports:** Filtered Sales, Product Performance, Customer Segmentation, Inventory Status, and Cleaned Datasets.
2. **Multi-Sheet Formatted Excel (`.xlsx`):** Professional workbook generated via `openpyxl` with Burgundy headers, borders, number formatting, and 6 organized tabs.
3. **Executive PDF Summary Dossier:** Multi-page executive brief compiled via `reportlab` featuring brand identity, date filters, KPI matrices, top products, AI business recommendations, and an evaluator sign-off block.

---

## 🎓 7. College Viva & Presentation Tips

When presenting this project to faculty or examiners, highlight the complete analytical pipeline:
1. **Show the Problem:** Fashion retail requires rapid merchandising decisions, but data is usually trapped in disjointed sales and inventory spreadsheets.
2. **Demonstrate Data Cleaning & Health Audit:** Show how the system ingests messy data, audits missing values, and safely cleans anomalies.
3. **Demonstrate Dynamic Interactivity:** Change the date filter (e.g., from *All Time* to *Last 30 Days*) and show how all 6 KPI cards, spline charts, and inventory run rates update instantaneously.
4. **Highlight the Recommendations Page:** Explain that the recommendations are not hardcoded or generated by fake text; they are derived from real mathematical inequalities and statistical percentiles.
5. **Download the PDF Dossier:** Show the generated executive PDF with your college and student credentials directly included on the cover!
