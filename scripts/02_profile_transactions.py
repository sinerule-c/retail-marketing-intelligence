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

# 9. Investigate zero quantities and zero sales

zero_qty = df["QUANTITY"] == 0
zero_sales = df["SALES_VALUE"] == 0

print("\nZERO QUANTITY AND SALES INVESTIGATION:")

print(
    "Both quantity and sales are zero:",
    (zero_qty & zero_sales).sum()
)

print(
    "Zero quantity, postive sales:",
    (zero_qty & ~zero_sales).sum()
)

print(
    "Positive quantity, zero sales:",
    (~zero_qty & zero_sales).sum()
)

# 10. Investigate zero quantity with positive sales

unusual_records = df[
    (df["QUANTITY"] == 0) &
    (df["SALES_VALUE"] > 0)
]

print("\nZERO QUANTITY WITH POSITIVE SALES:")
print(unusual_records.head(10).to_string(index=False))

tiny_sales = unusual_records[unusual_records["SALES_VALUE"] < 0.00001]

print("\nExtremely small positive sales:", len(tiny_sales))

print(tiny_sales[["PRODUCT_ID", "SALES_VALUE"]].head(10).to_string(index=False))

for value in tiny_sales["SALES_VALUE"].head(10):
    print(repr(value))

# Investigate zero-quantity records with meaningful positive sales

meaningful_sales = unusual_records[unusual_records["SALES_VALUE"].round(2) > 0]

print("\nZero quantity with positive sales after rounding:")
print(len(meaningful_sales))

print("\nFIRST 10 RECORDS:")
print(meaningful_sales[["PRODUCT_ID", "QUANTITY", "SALES_VALUE"]].head(10).to_string(index=False))

print("\n")
print(products[products["PRODUCT_ID"] == 866871].to_string(index=False))

# Join unusual transactions with product information
unusual_with_products = meaningful_sales.merge(
    products,
    on="PRODUCT_ID",
    how="left"
)

# Count unusual transactions by department
print(unusual_with_products["DEPARTMENT"].value_counts(dropna=False))

# 11. Examine unusual transactions with the highest sales

print("\nTOP 10 ZERO-QUANTITY TRANSACTIONS BY SALES:")

print(unusual_with_products[
    ["PRODUCT_ID", "DEPARTMENT", "SUB_COMMODITY_DESC", "QUANTITY", "SALES_VALUE"]
    ]
    .sort_values("SALES_VALUE", ascending=False)
    .head(10)
    .to_string(index=False)
)

# 12. Investigate positive quantity with zero sales

zero_sales_records = df[
    (df["QUANTITY"] > 0) &
    (df["SALES_VALUE"] == 0)
]

print("\nPOSITIVE QUANTITY WITH ZERO SALES:")

print(
    zero_sales_records[
        ["PRODUCT_ID", "QUANTITY", "SALES_VALUE", "RETAIL_DISC", "COUPON_DISC", "COUPON_MATCH_DISC"]
    ].head(10).to_string(index=False)
)

# 13. Investigate discount patterns in zero-sales records

print("\nZERO-SALES DISCOUNT ANALYSIS:")

print("Records with retailer discounts:", (zero_sales_records["RETAIL_DISC"] < 0).sum())

print("Records with manufacturer coupons:", (zero_sales_records["COUPON_DISC"] != 0).sum())

no_discounts = (
    (zero_sales_records["RETAIL_DISC"] == 0) &
    (zero_sales_records["COUPON_DISC"] == 0) &
    (zero_sales_records["COUPON_MATCH_DISC"] == 0)
)

print("Records with no recorded discounts:", no_discounts.sum())

# 14. Investigate zero-sales records without discounts

no_discount_records = zero_sales_records[no_discounts]

no_discount_products = no_discount_records.merge(
    products,
    on="PRODUCT_ID",
    how="left"
)

print("\nZERO SALES WITHOUT DISCOUNTS BY DEPARTMENT:")

print(no_discount_products["DEPARTMENT"].value_counts(dropna=False))

# 15. Investigate zero-sales records in the coupon department

coupon_records = no_discount_products[no_discount_products["DEPARTMENT"] == "COUP/STR & MFG"]

print("\nCOUPON DEPARTMENT RECORDS:")

print(coupon_records[["PRODUCT_ID", "COMMODITY_DESC", "SUB_COMMODITY_DESC", "QUANTITY", "SALES_VALUE"]].head(10).to_string(index=False))

# 16. Investigate grocery records with zero sales

grocery_records = no_discount_products[no_discount_products["DEPARTMENT"] == "GROCERY"]

print("\nGROCERY RECORDS WITH ZERO SALES:")

print(grocery_records[["PRODUCT_ID", "COMMODITY_DESC", "SUB_COMMODITY_DESC", "QUANTITY", "SALES_VALUE"]].head(10).to_string(index=False))

# 17. Identify grocery categories with zero sales

print("\nZERO-SALES GROCERY COMMODITIES:")

print(grocery_records["COMMODITY_DESC"].value_counts(dropna=False))

# 18. Investigate whether zero-sales snacks are sold normally

# Identify snack products with zero-sales records
snack_records = grocery_records[grocery_records["COMMODITY_DESC"] == "BAG SNACKS"]

snack_ids = snack_records["PRODUCT_ID"].unique()

# Find all transactions involving these products
snack_transactions = df[df["PRODUCT_ID"].isin(snack_ids)]

print("Distinct snack products:", len(snack_ids))

print("Products also sold for positive amounts:",
      snack_transactions.loc[
          snack_transactions["SALES_VALUE"] > 0,
          "PRODUCT_ID"
      ].nunique()
)

print("Positive-sales transaction lines:", (snack_transactions["SALES_VALUE"] > 0).sum())

# 19. Investigate discount values

discount_cols = ["RETAIL_DISC", "COUPON_DISC", "COUPON_MATCH_DISC"]

print("\nDISCOUNT SUMMARY:")
print(df[discount_cols].describe())

for col in discount_cols:
    print(f"\n{col}")
    print("Negative values:", (df[col] < 0).sum())
    print("Zero values:", (df[col] == 0).sum())
    print("Positive values:", (df[col] > 0).sum())

# 20. Investigate positive retailer discounts

positive_retail = df[df["RETAIL_DISC"] > 0]

print("\nPOSITIVE RETAILER DISCOUNTS:")
print("Number of records:", len(positive_retail))

print(
    positive_retail[
        ["PRODUCT_ID", "QUANTITY", "SALES_VALUE", "RETAIL_DISC", "COUPON_DISC", "COUPON_MATCH_DISC"]
    ].sort_values("RETAIL_DISC", ascending=False).head(10).to_string(index=False)
)

# 21. Examine positive retailer discounts with zero quantities

zero_qty_positive_retail = positive_retail[
    positive_retail["QUANTITY"] == 0
]

print("Total positive retail discounts:", len(positive_retail))

print("Positive retail discounts with zero quantity:", len(zero_qty_positive_retail))

print("Zero-quantity records where retail discount equals sales:",
      (zero_qty_positive_retail["RETAIL_DISC"].round(2)
       == zero_qty_positive_retail["SALES_VALUE"].round(2)
     ).sum()
)

# 22. Investigate exceptions to the positive discount pattern

exceptions = positive_retail[
    (positive_retail["QUANTITY"] > 0) |
    (
        (positive_retail["QUANTITY"] == 0) &
        (positive_retail["RETAIL_DISC"].round(2) != positive_retail["SALES_VALUE"].round(2))
    )
]

print("\nPOSITIVE DISCOUNT EXCEPTIONS:")

print(
    exceptions[
        ["PRODUCT_ID", "QUANTITY", "SALES_VALUE", "RETAIL_DISC"]
    ].to_string(index=False)
)

# 23. Inspect positive discount exceptions at full precision

print("\nPOSITIVE DISCOUNT EXCEPTIONS - FULL PRECISION:")

print(
    exceptions[["PRODUCT_ID", "QUANTITY", "SALES_VALUE", "RETAIL_DISC"]].to_string(index=False, float_format=lambda x: f"{x:.17g}")
)

# 24. Distinguish meaningful positive discounts from precision artefacts

retail_disc = df["RETAIL_DISC"]

print("Positive discounts before rounding:", (retail_disc > 0).sum())

print("Positive discounts after rounding:", (retail_disc.round(2) > 0).sum())

print("Tiny positive discounts:", ((retail_disc > 0) & (retail_disc.round(2) == 0)).sum())

# 25. Investigate transaction day and week ranges

for col in ["DAY", "WEEK_NO"]:
    print(f"\n{col} SUMMARY:")
    print("Minimum:", df[col].min())
    print("Maximum:", df[col].max())
    print("Unique values:", df[col].nunique())
    print("Zero or negative values:", (df[col] <= 0).sum())

# 26. Check consistency between DAY and WEEK_NO

expected_week = ((df["DAY"] - 1) // 7) + 1

week_mismatch = df["WEEK_NO"] != expected_week

print("\nDAY AND WEEK CONSISTENCY:")
print("Mismatched records:", week_mismatch.sum())

# 27. Investigate actual week boundaries

week_ranges = df.groupby("WEEK_NO")["DAY"].agg(
    first_day="min",
    last_day="max",
    observed_days="nunique"
)

print("\nACTUAL WEEK BOUNDARIES:")
print(week_ranges.head(10))

# 28. Validate DAY and WEEK_NO using observed week boundaries

expected_week = ((df["DAY"] + 1) // 7) + 1

week_mismatch = df["WEEK_NO"] != expected_week

print("\nREVISED WEEK VALIDATION:")
print("Mismatched records:", week_mismatch.sum())

# 29. Validate transaction times

print("\nTRANSACTION TIME SUMMARY:")
print("Minimum:", df["TRANS_TIME"].min())
print("Maximum:", df["TRANS_TIME"].max())

# Extract hours and minutes
hours = df["TRANS_TIME"] // 100
minutes = df["TRANS_TIME"] % 100

# Identify invalid times
invalid_time = (
    (hours < 0) |
    (hours > 23) |
    (minutes < 0) |
    (minutes > 59)
)

print("Invalid transaction times:", invalid_time.sum())