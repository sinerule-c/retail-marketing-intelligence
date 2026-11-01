import pandas as pd

# Load coupon dataset
coupons = pd.read_csv("data/raw/coupon.csv")

print("\nCOUPON DATASET INSPECTION:")

print("Dataset dimensions:")
print(coupons.shape)

print("\nColumn names:")
print(coupons.columns.tolist())

print("\nFirst 10 rows:")
print(coupons.head(10).to_string(index=False))

print("\nData types:")
print(coupons.dtypes)


# Check coupon dataset granularity

print("\nCOUPON GRANULARITY SUMMARY:")

print("Unique coupon IDs:", coupons["COUPON_UPC"].nunique())

print("Unique products:", coupons["PRODUCT_ID"].nunique())

print("Unique campaigns:", coupons["CAMPAIGN"].nunique())

print("Duplicate coupon-product-campaign combinations:", coupons.duplicated(
    subset=["COUPON_UPC", "PRODUCT_ID", "CAMPAIGN"]).sum())

# Investigate duplicate coupon combinations

coupon_counts = (
    coupons.groupby(["COUPON_UPC", "PRODUCT_ID", "CAMPAIGN"])
    .size()
    .reset_index(name="occurrences")
)

repeated = coupon_counts[coupon_counts["occurrences"] > 1]

print("\nCOUPON DUPLICATE INVESTIGATION:")

print("Distinct combinations repeated:", len(repeated))

print("Maximum occurrences of one combination:", repeated["occurrences"].max())

print("\nTop 10 repeated combinations:")
print(repeated.sort_values("occurrences", ascending=False).head(10).to_string(index=False))


# 3. Investigate duplicate records by campaign

coupon_counts["extra_duplicates"] = (coupon_counts["occurrences"] - 1)

duplicates_by_campaign = (
    coupon_counts.groupby("CAMPAIGN")["extra_duplicates"]
    .sum()
    .sort_values(ascending=False))

print("\nDUPLICATE RECORDS BY CAMPAIGN:")

print(duplicates_by_campaign.head(10).to_string())

print("\nTotal extra duplicate rows:", duplicates_by_campaign.sum())

# 4. Calculate duplication rates by campaign

campaign_totals = coupons.groupby("CAMPAIGN").size()

campaign_summary = pd.DataFrame({
    "total_rows": campaign_totals,
    "extra_duplicates": duplicates_by_campaign
})

campaign_summary["duplicate_rate_pct"] = (
    campaign_summary["extra_duplicates"] / campaign_summary["total_rows"] * 100
).round(2)

print("\nDUPLICATION RATES BY CAMPAIGN:")

print(campaign_summary.sort_values(
    "duplicate_rate_pct", 
    ascending=False).head(10).to_string()
)