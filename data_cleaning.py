"""
Data Cleaning & Quality Diagnostics Module
Provides automated audits, data validation, and safe cleaning routines.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

def generate_data_health_profile(df: pd.DataFrame, entity_name: str = "Dataset") -> Dict[str, Any]:
    """
    Computes a comprehensive data quality and health audit report for a DataFrame.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    
    # 1. Missing values
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / total_rows * 100).round(2) if total_rows > 0 else 0
    missing_summary = pd.DataFrame({
        "Column": df.columns,
        "Missing_Count": missing_counts.values,
        "Missing_Percentage": missing_pct.values,
        "Data_Type": [str(df[col].dtype) for col in df.columns]
    })
    
    # 2. Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    
    # 3. Anomaly / Invalid Value checks
    invalid_checks = []
    
    # Check numeric columns for negative or zero anomalies
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        col_lower = col.lower()
        if any(term in col_lower for term in ["price", "amount", "total", "cost"]):
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                invalid_checks.append({
                    "Issue": f"Negative currency values in '{col}'",
                    "Affected_Rows": neg_count,
                    "Severity": "Critical"
                })
        elif any(term in col_lower for term in ["quantity", "qty", "stock"]):
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                invalid_checks.append({
                    "Issue": f"Negative counts in '{col}'",
                    "Affected_Rows": neg_count,
                    "Severity": "High"
                })
        elif "age" in col_lower:
            invalid_age = int(((df[col] < 12) | (df[col] > 110)).sum())
            if invalid_age > 0:
                invalid_checks.append({
                    "Issue": f"Unrealistic age entries (<12 or >110) in '{col}'",
                    "Affected_Rows": invalid_age,
                    "Severity": "Medium"
                })

    # Check date columns
    date_cols = [c for c in df.columns if "date" in c.lower()]
    for col in date_cols:
        parsed_dates = pd.to_datetime(df[col], errors="coerce")
        nat_count = int(parsed_dates.isna().sum() - df[col].isna().sum())
        if nat_count > 0:
            invalid_checks.append({
                "Issue": f"Unparseable date formats in '{col}'",
                "Affected_Rows": nat_count,
                "Severity": "High"
            })

    # Calculate overall data health score (0 - 100)
    health_penalty = 0
    if total_rows > 0:
        total_cells = total_rows * total_cols
        missing_cells = int(missing_counts.sum())
        missing_rate = missing_cells / total_cells
        health_penalty += min(40, missing_rate * 100)
        
        dup_rate = duplicate_rows / total_rows
        health_penalty += min(30, dup_rate * 100)
        
        for chk in invalid_checks:
            health_penalty += min(10, (chk["Affected_Rows"] / total_rows) * 100)
            
    health_score = max(0, min(100, int(100 - health_penalty)))
    
    return {
        "entity_name": entity_name,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "missing_summary": missing_summary,
        "total_missing_cells": int(missing_counts.sum()),
        "duplicate_rows": duplicate_rows,
        "invalid_checks": invalid_checks,
        "health_score": health_score
    }

def clean_dataset_safely(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    fill_missing_numeric: str = "median",
    fill_missing_categorical: str = "mode",
    filter_negative_values: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Applies non-destructive data cleaning based on user configuration.
    Returns cleaned DataFrame and an audit changelog.
    """
    cleaned = df.copy()
    changelog = []
    
    initial_rows = len(cleaned)
    
    # 1. Remove duplicate rows
    if remove_duplicates:
        dups_count = int(cleaned.duplicated().sum())
        if dups_count > 0:
            cleaned = cleaned.drop_duplicates().reset_index(drop=True)
            changelog.append(f"Removed {dups_count} duplicate row(s).")
            
    # 2. Date parsing and correction
    date_cols = [c for c in cleaned.columns if "date" in c.lower()]
    for col in date_cols:
        parsed = pd.to_datetime(cleaned[col], errors="coerce")
        bad_dates = parsed.isna().sum() - cleaned[col].isna().sum()
        if bad_dates > 0:
            changelog.append(f"Standardized dates in '{col}'. Coerced {bad_dates} invalid date(s).")
        cleaned[col] = parsed

    # 3. Numeric sanitation & imputation
    num_cols = cleaned.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        # Negative value filter
        if filter_negative_values:
            neg_mask = cleaned[col] < 0
            neg_count = int(neg_mask.sum())
            if neg_count > 0:
                cleaned.loc[neg_mask, col] = np.abs(cleaned.loc[neg_mask, col])
                changelog.append(f"Converted {neg_count} negative value(s) in '{col}' to absolute positive.")

        # Missing values in numeric
        nan_count = int(cleaned[col].isna().sum())
        if nan_count > 0:
            if fill_missing_numeric == "median":
                med_val = cleaned[col].median()
                cleaned[col] = cleaned[col].fillna(med_val)
                changelog.append(f"Imputed {nan_count} missing value(s) in '{col}' with column median ({med_val:.2f}).")
            elif fill_missing_numeric == "mean":
                mean_val = cleaned[col].mean()
                cleaned[col] = cleaned[col].fillna(mean_val)
                changelog.append(f"Imputed {nan_count} missing value(s) in '{col}' with column mean ({mean_val:.2f}).")
            elif fill_missing_numeric == "zero":
                cleaned[col] = cleaned[col].fillna(0)
                changelog.append(f"Imputed {nan_count} missing value(s) in '{col}' with 0.")

    # 4. Categorical missing values
    cat_cols = cleaned.select_dtypes(include=["object", "string", "category"]).columns
    for col in cat_cols:
        nan_count = int(cleaned[col].isna().sum())
        if nan_count > 0:
            if fill_missing_categorical == "mode":
                mode_series = cleaned[col].mode()
                mode_val = mode_series[0] if not mode_series.empty else "Unknown"
                cleaned[col] = cleaned[col].fillna(mode_val)
                changelog.append(f"Imputed {nan_count} missing value(s) in '{col}' with mode ('{mode_val}').")
            else:
                cleaned[col] = cleaned[col].fillna("Unknown")
                changelog.append(f"Imputed {nan_count} missing value(s) in '{col}' with 'Unknown'.")

    final_rows = len(cleaned)
    audit = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "rows_removed": initial_rows - final_rows,
        "changelog": changelog
    }
    
    return cleaned, audit
