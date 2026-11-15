"""
Data Generator for Fashion Brand Analytics
Generates realistic, internally consistent synthetic datasets for a luxury/contemporary fashion brand.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_fashion_dataset(seed: int = 42, output_dir: str = None):
    random.seed(seed)
    np.random.seed(seed)

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    os.makedirs(output_dir, exist_ok=True)

    # 1. CATALOG PRODUCTS (36 items across 6 luxury/contemporary categories)
    products_data = [
        # Men's Clothing
        {"Product_ID": "PRD-101", "Product_Name": "Oxford Cotton Classic Shirt", "Category": "Men's Clothing", "Brand": "Sartorial", "Size": "L", "Color": "White", "Selling_Price": 75.0, "Cost_Price": 32.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-102", "Product_Name": "Tailored Italian Wool Blazer", "Category": "Men's Clothing", "Brand": "Maison Royale", "Size": "40R", "Color": "Navy", "Selling_Price": 295.0, "Cost_Price": 125.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-103", "Product_Name": "Slim-Fit Chino Trousers", "Category": "Men's Clothing", "Brand": "Atelier V", "Size": "32", "Color": "Beige", "Selling_Price": 85.0, "Cost_Price": 36.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-104", "Product_Name": "Pure Cashmere Crewneck Sweater", "Category": "Men's Clothing", "Brand": "L'Aura Mode", "Size": "M", "Color": "Camel", "Selling_Price": 220.0, "Cost_Price": 92.0, "Reorder_Level": 12},
        {"Product_ID": "PRD-105", "Product_Name": "Linen Resort Cuban Collar Shirt", "Category": "Men's Clothing", "Brand": "Sartorial", "Size": "L", "Color": "Cream", "Selling_Price": 65.0, "Cost_Price": 28.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-106", "Product_Name": "Fine Merino Wool Polo", "Category": "Men's Clothing", "Brand": "Sartorial", "Size": "M", "Color": "Burgundy", "Selling_Price": 95.0, "Cost_Price": 40.0, "Reorder_Level": 12},

        # Women's Clothing
        {"Product_ID": "PRD-201", "Product_Name": "Silk Charmeuse Wrap Dress", "Category": "Women's Clothing", "Brand": "Maison Royale", "Size": "M", "Color": "Burgundy", "Selling_Price": 240.0, "Cost_Price": 102.0, "Reorder_Level": 12},
        {"Product_ID": "PRD-202", "Product_Name": "Double-Breasted Trench Coat", "Category": "Women's Clothing", "Brand": "Atelier V", "Size": "S", "Color": "Beige", "Selling_Price": 310.0, "Cost_Price": 135.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-203", "Product_Name": "Pleated Georgette Midi Skirt", "Category": "Women's Clothing", "Brand": "L'Aura Mode", "Size": "S", "Color": "Ivory", "Selling_Price": 110.0, "Cost_Price": 48.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-204", "Product_Name": "Structured Hourglass Blazer", "Category": "Women's Clothing", "Brand": "Maison Royale", "Size": "M", "Color": "Black", "Selling_Price": 280.0, "Cost_Price": 118.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-205", "Product_Name": "Velvet Midnight Evening Gown", "Category": "Women's Clothing", "Brand": "L'Aura Mode", "Size": "S", "Color": "Emerald", "Selling_Price": 360.0, "Cost_Price": 155.0, "Reorder_Level": 8},
        {"Product_ID": "PRD-206", "Product_Name": "Poplin Tiered Summer Dress", "Category": "Women's Clothing", "Brand": "Atelier V", "Size": "M", "Color": "Blush", "Selling_Price": 135.0, "Cost_Price": 58.0, "Reorder_Level": 15},

        # Footwear
        {"Product_ID": "PRD-301", "Product_Name": "Handmade Italian Leather Loafers", "Category": "Footwear", "Brand": "Sartorial", "Size": "9", "Color": "Cognac", "Selling_Price": 210.0, "Cost_Price": 88.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-302", "Product_Name": "Suede Chelsea Boots", "Category": "Footwear", "Brand": "Atelier V", "Size": "10", "Color": "Espresso", "Selling_Price": 225.0, "Cost_Price": 95.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-303", "Product_Name": "Minimalist Leather Court Sneakers", "Category": "Footwear", "Brand": "Atelier V", "Size": "9", "Color": "White", "Selling_Price": 150.0, "Cost_Price": 62.0, "Reorder_Level": 18},
        {"Product_ID": "PRD-304", "Product_Name": "Velvet Stiletto Evening Pumps", "Category": "Footwear", "Brand": "L'Aura Mode", "Size": "7", "Color": "Burgundy", "Selling_Price": 195.0, "Cost_Price": 82.0, "Reorder_Level": 8},
        {"Product_ID": "PRD-305", "Product_Name": "Burnished Suede Derby Shoes", "Category": "Footwear", "Brand": "Sartorial", "Size": "10", "Color": "Sand", "Selling_Price": 185.0, "Cost_Price": 78.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-306", "Product_Name": "Strappy Metallic Heeled Sandals", "Category": "Footwear", "Brand": "Maison Royale", "Size": "8", "Color": "Gold", "Selling_Price": 170.0, "Cost_Price": 72.0, "Reorder_Level": 8},

        # Accessories
        {"Product_ID": "PRD-401", "Product_Name": "Silk Twill Monogram Scarf", "Category": "Accessories", "Brand": "Maison Royale", "Size": "Free Size", "Color": "Burgundy Print", "Selling_Price": 125.0, "Cost_Price": 45.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-402", "Product_Name": "Reversible Full-Grain Leather Belt", "Category": "Accessories", "Brand": "Sartorial", "Size": "34", "Color": "Black/Brown", "Selling_Price": 80.0, "Cost_Price": 30.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-403", "Product_Name": "Ribbed Cashmere Beanie", "Category": "Accessories", "Brand": "L'Aura Mode", "Size": "Free Size", "Color": "Oatmeal", "Selling_Price": 70.0, "Cost_Price": 26.0, "Reorder_Level": 15},
        {"Product_ID": "PRD-404", "Product_Name": "Acetate Polarized Sunglasses", "Category": "Accessories", "Brand": "Atelier V", "Size": "Free Size", "Color": "Tortoise", "Selling_Price": 145.0, "Cost_Price": 52.0, "Reorder_Level": 12},
        {"Product_ID": "PRD-405", "Product_Name": "Minimalist Saffiano Cardholder", "Category": "Accessories", "Brand": "Maison Royale", "Size": "Free Size", "Color": "Navy", "Selling_Price": 55.0, "Cost_Price": 18.0, "Reorder_Level": 20},
        {"Product_ID": "PRD-406", "Product_Name": "Knitted Cashmere Muffler", "Category": "Accessories", "Brand": "L'Aura Mode", "Size": "Free Size", "Color": "Camel", "Selling_Price": 115.0, "Cost_Price": 44.0, "Reorder_Level": 12},

        # Bags
        {"Product_ID": "PRD-501", "Product_Name": "Quilted Lambskin Crossbody Bag", "Category": "Bags", "Brand": "Maison Royale", "Size": "Medium", "Color": "Burgundy", "Selling_Price": 320.0, "Cost_Price": 138.0, "Reorder_Level": 8},
        {"Product_ID": "PRD-502", "Product_Name": "Structured Leather Work Tote", "Category": "Bags", "Brand": "Atelier V", "Size": "Large", "Color": "Tan", "Selling_Price": 285.0, "Cost_Price": 120.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-503", "Product_Name": "Envelope Evening Saffiano Clutch", "Category": "Bags", "Brand": "L'Aura Mode", "Size": "Small", "Color": "Champagne", "Selling_Price": 160.0, "Cost_Price": 65.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-504", "Product_Name": "Heritage Leather Weekend Duffle", "Category": "Bags", "Brand": "Sartorial", "Size": "Large", "Color": "Espresso", "Selling_Price": 340.0, "Cost_Price": 145.0, "Reorder_Level": 6},
        {"Product_ID": "PRD-505", "Product_Name": "Heavy Canvas Everyday Shopper", "Category": "Bags", "Brand": "Atelier V", "Size": "Large", "Color": "Natural", "Selling_Price": 75.0, "Cost_Price": 28.0, "Reorder_Level": 20},
        {"Product_ID": "PRD-506", "Product_Name": "Compact Crescent Saddle Bag", "Category": "Bags", "Brand": "Maison Royale", "Size": "Medium", "Color": "Forest Green", "Selling_Price": 210.0, "Cost_Price": 88.0, "Reorder_Level": 10},

        # Ethnic Wear
        {"Product_ID": "PRD-601", "Product_Name": "Hand-Embroidered Chanderi Kurta Set", "Category": "Ethnic Wear", "Brand": "Heritage Silk", "Size": "M", "Color": "Ivory Gold", "Selling_Price": 180.0, "Cost_Price": 75.0, "Reorder_Level": 12},
        {"Product_ID": "PRD-602", "Product_Name": "Chanderi Pure Silk Festive Saree", "Category": "Ethnic Wear", "Brand": "Heritage Silk", "Size": "Free Size", "Color": "Royal Burgundy", "Selling_Price": 230.0, "Cost_Price": 95.0, "Reorder_Level": 10},
        {"Product_ID": "PRD-603", "Product_Name": "Handloom Tussar Silk Nehru Jacket", "Category": "Ethnic Wear", "Brand": "Heritage Silk", "Size": "40", "Color": "Wine", "Selling_Price": 140.0, "Cost_Price": 58.0, "Reorder_Level": 12},
        {"Product_ID": "PRD-604", "Product_Name": "Georgette Anarkali Festive Gown", "Category": "Ethnic Wear", "Brand": "Heritage Silk", "Size": "S", "Color": "Deep Emerald", "Selling_Price": 275.0, "Cost_Price": 115.0, "Reorder_Level": 8},
        {"Product_ID": "PRD-605", "Product_Name": "Brocade Jacquard Festive Sherwani", "Category": "Ethnic Wear", "Brand": "Heritage Silk", "Size": "42", "Color": "Midnight Wine", "Selling_Price": 350.0, "Cost_Price": 145.0, "Reorder_Level": 6},
        {"Product_ID": "PRD-606", "Product_Name": "Banarasi Zari Border Dupatta", "Category": "Ethnic Wear", "Brand": "Heritage Silk", "Size": "Free Size", "Color": "Scarlet", "Selling_Price": 95.0, "Cost_Price": 38.0, "Reorder_Level": 15},
    ]

    products_df = pd.DataFrame(products_data)

    # 2. CUSTOMERS (120 realistic customers)
    first_names = [
        "Aarav", "Aditi", "Alexander", "Amara", "Ananya", "Arjun", "Chloe", "David",
        "Dev", "Diya", "Eleanor", "Ethan", "Fatima", "Gabriel", "Grace", "Hannah",
        "Ishaan", "Isabella", "James", "Kavya", "Leo", "Lucas", "Maya", "Meera",
        "Michael", "Mira", "Nathan", "Neha", "Noah", "Oliver", "Priya", "Rahul",
        "Rhea", "Rohan", "Saanvi", "Samira", "Siddharth", "Sophia", "Tara", "Varun",
        "Victoria", "Vihaan", "Vikram", "Zara", "Liam", "Emma", "Olivia", "Ava",
        "Sebastian", "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail", "Emily"
    ]
    last_names = [
        "Sharma", "Patel", "Verma", "Kapoor", "Vance", "Wright", "Martinez", "Sterling",
        "Chen", "Dupont", "Sinclair", "Mehta", "Reddy", "Nair", "Chopra", "Gupta",
        "Joshi", "Bose", "Kulkarni", "Menon", "Deshmukh", "Iyer", "Rao", "Nath",
        "Castillo", "Moreau", "Novak", "Lindqvist", "Hayashi", "Bianchi", "Fontana"
    ]
    regions = ["North", "South", "West", "East", "Central"]
    region_weights = [0.30, 0.25, 0.22, 0.15, 0.08]
    genders = ["Female", "Male", "Non-Binary"]
    gender_weights = [0.54, 0.43, 0.03]

    customers_data = []
    base_date = datetime(2025, 1, 1)

    for i in range(1, 121):
        c_id = f"CUST-{1000 + i}"
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        name = f"{f_name} {l_name}"
        gender = np.random.choice(genders, p=gender_weights)
        age = int(np.random.normal(35, 10))
        age = max(20, min(65, age))
        reg_days_ago = random.randint(30, 720)
        reg_date = (base_date - timedelta(days=reg_days_ago)).strftime("%Y-%m-%d")
        region = np.random.choice(regions, p=region_weights)

        customers_data.append({
            "Customer_ID": c_id,
            "Customer_Name": name,
            "Age": age,
            "Gender": gender,
            "Region": region,
            "Registration_Date": reg_date
        })

    customers_df = pd.DataFrame(customers_data)

    # 3. SALES TRANSACTIONS (1,250 transactions across 12 months)
    # Give products a realistic popularity curve (best-sellers get more orders)
    # e.g., P101, P201, P303, P401, P501, P602 have higher weights
    p_weights = []
    for p in products_data:
        pid = p["Product_ID"]
        if pid in ["PRD-201", "PRD-501", "PRD-102", "PRD-303", "PRD-602", "PRD-401"]:
            p_weights.append(3.5) # Top sellers
        elif pid in ["PRD-101", "PRD-202", "PRD-301", "PRD-405", "PRD-601", "PRD-502"]:
            p_weights.append(2.2) # Strong performers
        elif pid in ["PRD-105", "PRD-305", "PRD-403", "PRD-505", "PRD-606"]:
            p_weights.append(0.6) # Slower movers
        elif pid in ["PRD-205", "PRD-605", "PRD-306"]:
            p_weights.append(0.4) # Niche / High ticket underperformers
        else:
            p_weights.append(1.2)
    p_weights = np.array(p_weights) / sum(p_weights)

    # Customer weighting (Pareto distribution: 20% of customers make 50% of purchases)
    c_weights = np.random.pareto(a=2.0, size=len(customers_data)) + 0.2
    c_weights = c_weights / sum(c_weights)

    payment_methods = ["Credit Card", "UPI", "Debit Card", "Net Banking", "Cash on Delivery"]
    payment_weights = [0.42, 0.26, 0.18, 0.09, 0.05]

    transactions = []
    start_date = datetime(2025, 11, 15) # Up to current anchor date
    num_transactions = 1250

    product_lookup = {p["Product_ID"]: p for p in products_data}
    customer_lookup = {c["Customer_ID"]: c for c in customers_data}

    # Tracking units sold per product for consistent inventory
    units_sold_per_product = {p["Product_ID"]: 0 for p in products_data}

    for order_num in range(1, num_transactions + 1):
        order_id = f"ORD-{20250000 + order_num}"
        
        # Date distribution: slightly more sales on weekends and Q4 holiday season
        days_back = int(np.random.beta(a=1.8, b=1.2) * 365)
        trans_date = start_date - timedelta(days=days_back)
        
        c_idx = np.random.choice(len(customers_data), p=c_weights)
        customer = customers_data[c_idx]
        cust_id = customer["Customer_ID"]
        
        p_idx = np.random.choice(len(products_data), p=p_weights)
        prod = products_data[p_idx]
        prod_id = prod["Product_ID"]
        
        qty = int(np.random.choice([1, 2, 3, 4], p=[0.72, 0.20, 0.06, 0.02]))
        units_sold_per_product[prod_id] += qty

        unit_price = prod["Selling_Price"]
        
        # Realistic discount: 0% mostly, with 5%, 10%, 15%, 20% during promos
        discount_pct = float(np.random.choice([0, 5, 10, 15, 20], p=[0.55, 0.20, 0.15, 0.07, 0.03]))
        
        subtotal = qty * unit_price
        discount_amount = round(subtotal * (discount_pct / 100.0), 2)
        total_amount = round(subtotal - discount_amount, 2)
        
        payment = np.random.choice(payment_methods, p=payment_weights)
        
        # Region usually matches customer region (95%) or gift order elsewhere (5%)
        if random.random() < 0.95:
            region = customer["Region"]
        else:
            region = np.random.choice(regions)

        transactions.append({
            "Order_ID": order_id,
            "Order_Date": trans_date.strftime("%Y-%m-%d"),
            "Customer_ID": cust_id,
            "Product_ID": prod_id,
            "Quantity": qty,
            "Unit_Price": unit_price,
            "Discount": discount_pct,
            "Total_Amount": total_amount,
            "Payment_Method": payment,
            "Region": region
        })

    # Sort transactions chronologically
    sales_df = pd.DataFrame(transactions)
    sales_df = sales_df.sort_values("Order_Date").reset_index(drop=True)

    # 4. INVENTORY STOCK CONSISTENCY
    # Ensure realistic stock states:
    # - Low Stock items (< Reorder Level)
    # - Out of Stock items (0)
    # - Overstocked items (> 100 with low sales)
    # - In Stock items (healthy)
    available_stocks = []
    for p in products_data:
        pid = p["Product_ID"]
        sold = units_sold_per_product[pid]
        reorder_lvl = p["Reorder_Level"]
        
        # Target specific status profiles:
        if pid in ["PRD-205", "PRD-306"]:  # Out of stock
            avail = 0
        elif pid in ["PRD-102", "PRD-201", "PRD-501", "PRD-602"]: # Low stock (Best sellers near depletion)
            avail = random.randint(3, reorder_lvl - 2)
        elif pid in ["PRD-105", "PRD-305", "PRD-505"]: # Overstocked slow movers
            avail = random.randint(120, 175)
        else: # Normal healthy stock
            avail = random.randint(reorder_lvl + 8, reorder_lvl + 65)
            
        available_stocks.append(avail)

    products_df["Available_Stock"] = available_stocks

    # Save CSVs
    sales_csv_path = os.path.join(output_dir, "sales.csv")
    products_csv_path = os.path.join(output_dir, "products.csv")
    customers_csv_path = os.path.join(output_dir, "customers.csv")
    
    sales_df.to_csv(sales_csv_path, index=False)
    products_df.to_csv(products_csv_path, index=False)
    customers_df.to_csv(customers_csv_path, index=False)

    # Also generate a consolidated multi-sheet Excel file for demo / downloads
    excel_path = os.path.join(output_dir, "fashion_brand_demo.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        sales_df.to_excel(writer, sheet_name="Sales_Transactions", index=False)
        products_df.to_excel(writer, sheet_name="Products_Catalog", index=False)
        customers_df.to_excel(writer, sheet_name="Customers", index=False)

    print(f"Data generation complete!")
    print(f"Sales: {len(sales_df)} rows -> {sales_csv_path}")
    print(f"Products: {len(products_df)} rows -> {products_csv_path}")
    print(f"Customers: {len(customers_df)} rows -> {customers_csv_path}")
    print(f"Excel Demo: {excel_path}")

    return sales_df, products_df, customers_df

if __name__ == "__main__":
    generate_fashion_dataset()
