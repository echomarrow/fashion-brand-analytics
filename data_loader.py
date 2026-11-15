"""
Data Loader & Management Module
Handles dataset loading, merging, validation, and schema mapping.
"""

import os
import re
from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np

# Canonical expected schemas
REQUIRED_COLUMNS = {
    "sales": ["Order_ID", "Order_Date", "Customer_ID", "Product_ID", "Quantity", "Unit_Price", "Total_Amount"],
    "products": ["Product_ID", "Product_Name", "Category", "Selling_Price", "Available_Stock"],
    "customers": ["Customer_ID", "Customer_Name", "Age", "Gender", "Region"]
}

# Fuzzy column mapping rules for custom uploaded files
COLUMN_ALIASES = {
    # Sales
    "order_id": ["orderid", "order_no", "invoice_no", "transaction_id", "order_num"],
    "order_date": ["orderdate", "date", "transaction_date", "invoice_date", "purchase_date"],
    "customer_id": ["customerid", "cust_id", "client_id", "user_id"],
    "product_id": ["productid", "item_id", "sku", "item_code"],
    "quantity": ["qty", "units", "quantity_sold", "units_sold"],
    "unit_price": ["unitprice", "price", "mrp", "item_price"],
    "discount": ["discount_pct", "discount_percentage", "discount_amt", "rebate"],
    "total_amount": ["totalamount", "total", "revenue", "sale_amount", "net_amount", "amount"],
    "payment_method": ["paymentmethod", "payment_type", "payment_mode", "payment"],
    "region": ["territory", "location", "zone", "state", "sales_region"],
    
    # Products
    "product_name": ["productname", "item_name", "title", "product_title"],
    "category": ["product_category", "department", "cat", "item_category"],
    "brand": ["brand_name", "label", "manufacturer"],
    "size": ["product_size", "fit"],
    "color": ["colour", "shade"],
    "selling_price": ["sellingprice", "price", "retail_price"],
    "cost_price": ["costprice", "cost", "wholesale_price"],
    "available_stock": ["availablestock", "current_stock", "stock", "quantity_in_stock", "inventory"],
    "reorder_level": ["reorderlevel", "threshold", "safety_stock", "reorder_point"],
    
    # Customers
    "customer_name": ["customername", "name", "full_name", "client_name"],
    "age": ["customer_age", "years"],
    "gender": ["sex"],
}

def get_sample_data_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def load_sample_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads default sample CSV datasets for sales, products, and customers."""
    sample_dir = get_sample_data_dir()
    sales_path = os.path.join(sample_dir, "sales.csv")
    products_path = os.path.join(sample_dir, "products.csv")
    customers_path = os.path.join(sample_dir, "customers.csv")
    
    if not (os.path.exists(sales_path) and os.path.exists(products_path) and os.path.exists(customers_path)):
        # Generate them on the fly if missing
        from generate_data import generate_fashion_dataset
        return generate_fashion_dataset(output_dir=sample_dir)
        
    sales_df = pd.read_csv(sales_path)
    products_df = pd.read_csv(products_path)
    customers_df = pd.read_csv(customers_path)
    
    # Ensure types
    sales_df["Order_Date"] = pd.to_datetime(sales_df["Order_Date"])
    sales_df["Quantity"] = pd.to_numeric(sales_df["Quantity"], errors="coerce").fillna(1).astype(int)
    sales_df["Unit_Price"] = pd.to_numeric(sales_df["Unit_Price"], errors="coerce").fillna(0.0)
    sales_df["Total_Amount"] = pd.to_numeric(sales_df["Total_Amount"], errors="coerce").fillna(0.0)
    
    products_df["Selling_Price"] = pd.to_numeric(products_df["Selling_Price"], errors="coerce").fillna(0.0)
    products_df["Available_Stock"] = pd.to_numeric(products_df["Available_Stock"], errors="coerce").fillna(0).astype(int)
    if "Reorder_Level" in products_df.columns:
        products_df["Reorder_Level"] = pd.to_numeric(products_df["Reorder_Level"], errors="coerce").fillna(10).astype(int)
    
    customers_df["Age"] = pd.to_numeric(customers_df["Age"], errors="coerce").fillna(35).astype(int)
    
    return sales_df, products_df, customers_df

def auto_map_columns(df: pd.DataFrame, entity_type: str = "sales") -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Intelligently maps raw column names in uploaded files to standardized column names.
    """
    mapping = {}
    normalized_cols = {re.sub(r'[^a-zA-Z0-9]', '', col.lower()): col for col in df.columns}
    
    for standard_col, aliases in COLUMN_ALIASES.items():
        # Match standard col name directly
        clean_std = re.sub(r'[^a-zA-Z0-9]', '', standard_col.lower())
        matched = None
        
        if clean_std in normalized_cols:
            matched = normalized_cols[clean_std]
        else:
            for alias in aliases:
                clean_alias = re.sub(r'[^a-zA-Z0-9]', '', alias.lower())
                if clean_alias in normalized_cols:
                    matched = normalized_cols[clean_alias]
                    break
                    
        if matched:
            # Proper casing for standard columns
            proper_col = "_".join([w.capitalize() for w in standard_col.split("_")])
            # Special acronym cases
            proper_col = proper_col.replace("Id", "ID")
            mapping[matched] = proper_col

    renamed_df = df.rename(columns=mapping)
    return renamed_df, mapping

def validate_dataset_schema(df: pd.DataFrame, entity_type: str) -> Tuple[bool, list]:
    """
    Validates whether required columns exist in the DataFrame for the given entity.
    """
    required = REQUIRED_COLUMNS.get(entity_type, [])
    missing = [col for col in required if col not in df.columns]
    is_valid = len(missing) == 0
    return is_valid, missing

def merge_datasets(sales_df: pd.DataFrame, products_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Joins sales transactions with products catalog and customer demographic data.
    Ensures safe left join without losing unlinked transactions.
    """
    sales = sales_df.copy()
    if not np.issubdtype(sales["Order_Date"].dtype, np.datetime64):
        sales["Order_Date"] = pd.to_datetime(sales["Order_Date"], errors="coerce")
        
    merged = sales.merge(products_df, on="Product_ID", how="left", suffixes=("", "_prod"))
    merged = merged.merge(customers_df, on="Customer_ID", how="left", suffixes=("", "_cust"))
    
    # Fallback fills for unmapped fields if custom upload lacks full relational match
    if "Category" not in merged.columns or merged["Category"].isna().all():
        merged["Category"] = "General Apparel"
    else:
        merged["Category"] = merged["Category"].fillna("General Apparel")
        
    if "Product_Name" not in merged.columns or merged["Product_Name"].isna().all():
        merged["Product_Name"] = merged["Product_ID"]
    else:
        merged["Product_Name"] = merged["Product_Name"].fillna(merged["Product_ID"])

    if "Customer_Name" not in merged.columns or merged["Customer_Name"].isna().all():
        merged["Customer_Name"] = merged["Customer_ID"]
    else:
        merged["Customer_Name"] = merged["Customer_Name"].fillna(merged["Customer_ID"])

    if "Payment_Method" not in merged.columns:
        merged["Payment_Method"] = "Other"
    else:
        merged["Payment_Method"] = merged["Payment_Method"].fillna("Other")

    if "Region" not in merged.columns:
        merged["Region"] = "National"
    else:
        merged["Region"] = merged["Region"].fillna("National")

    # Ensure numeric columns
    merged["Quantity"] = pd.to_numeric(merged["Quantity"], errors="coerce").fillna(1).astype(int)
    merged["Total_Amount"] = pd.to_numeric(merged["Total_Amount"], errors="coerce").fillna(0.0)
    
    # Month, Year, Day of Week fields for instant charting
    merged["Month_Year"] = merged["Order_Date"].dt.strftime("%Y-%m")
    merged["Month_Name"] = merged["Order_Date"].dt.strftime("%b %Y")
    merged["Day_Name"] = merged["Order_Date"].dt.strftime("%A")
    merged["Year"] = merged["Order_Date"].dt.year
    
    return merged
