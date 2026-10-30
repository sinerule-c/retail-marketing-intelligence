import pandas as pd
pd.set_option("display.float_format", "{:,.2f}".format)

# Load the transaction dataset
df = pd.read_csv("data/raw/transaction_data.csv")

# 1. Dataset dimensions
print("DATASET DIMENSIONS:")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# 2. Date types
print("\nDATA TYPES:")
print(df.dtypes)

# 3. Missing values
print("\nMISSING VALUES:")
print(df.isnull().sum())

# 4. Duplicate rows
print("\nDUPLICATE ROWS:")
print("Exact duplicate rows:", df.duplicated().sum())

# 5. Quantity and sales value assessment
print("\nQUANTITY SUMMARY:")
print(df["QUANTITY"].describe())

print("\nSALES VALUE SUMMARY:")
print(df["SALES_VALUE"].describe())

print("\nPOTENTIALLY UNUSUAL VALUES:")
print("Zero quantity:", (df["QUANTITY"] == 0).sum())
print("Negative quantity:", (df["QUANTITY"] < 0).sum())
print("Zero sales:", (df["SALES_VALUE"] == 0).sum())
print("Negative sales:", (df["SALES_VALUE"] < 0).sum())

# 6. Investtigate unusually large quantities
top_quantities = df.nlargest(10, "QUANTITY")

print("\nTOP 10 LARGEST QUANTITIES:")
print(top_quantities[["PRODUCT_ID", "QUANTITY", "SALES_VALUE"]].to_string(index=False))

# 7. Investigate products with extreme quantities
products = pd.read_csv("data/raw/product.csv")

product_ids = [6534178, 6544236]

selected_products = products[products["PRODUCT_ID"].isin(product_ids)]

print("\nPRODUCTS WITH EXTREME QUANTITIES:")
print(selected_products.to_string(index=False))

# 8. Investigate the impact of gasoline transactions
gas_ids = products.loc[
    products["SUB_COMMODITY_DESC"] == "GASOLINE-REG UNLEADED",
    "PRODUCT_ID"
]

gas_mask = df["PRODUCT_ID"].isin(gas_ids)

print("\nGasoline records:", gas_mask.sum())

print(
    "Average quantity excluding gasoline:",
    df.loc[~gas_mask, "QUANTITY"].mean()
)

print(
    "Maximum quantity excluding gasoline:",
    df.loc[~gas_mask, "QUANTITY"].max()
)