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

# 5. Inspect coupon redemption dataset

redemptions = pd.read_csv("data/raw/coupon_redempt.csv")

print("\nCOUPON REDEMPTION DATASET:")

print("Dataset dimensions:")
print(redemptions.shape)

print("\nColumn names:")
print(redemptions.columns.tolist())

print("\nFirst 10 rows:")
print(redemptions.head(10).to_string(index=False))

print("\nData types:")
print(redemptions.dtypes)

# 6. Validate coupon redemption granularity

print("\nCOUPON REDEMPTION GRANULARITY:")

print("Unique households:", redemptions["household_key"].nunique())

print("Unique redeemed coupons:", redemptions["COUPON_UPC"].nunique())

print("Unique campaigns:", redemptions["CAMPAIGN"].nunique())

print("Exact duplicate redemption records:", redemptions.duplicated().sum())

# 7. Validate redeemed coupon-campaign combinations

eligible_pairs = coupons[["COUPON_UPC", "CAMPAIGN"]].drop_duplicates()

redemption_check = redemptions.merge(
    eligible_pairs,
    on=["COUPON_UPC", "CAMPAIGN"],
    how="left",
    indicator=True,
    validate="many_to_one"
)

unmatched = redemption_check["_merge"] == "left_only"

print("\nCOUPON REDEMPTION REFERENTIAL INTEGRITY:")

print("Redemption rows with unmatched coupon-campaign pairs:", unmatched.sum())

print("Distinct unmatched coupon-campaign pairs:",
      redemption_check.loc[unmatched, ["COUPON_UPC", "CAMPAIGN"]].drop_duplicates().shape[0])

# 8. Validate coupon redemption households

transactions = pd.read_csv("data/raw/transaction_data.csv", usecols=["household_key"])

campaigns = pd.read_csv("data/raw/campaign_table.csv", usecols=["household_key"])

# Get unique household IDs
redemption_households = redemptions["household_key"].drop_duplicates()

purchase_households = transactions["household_key"].drop_duplicates()

campaign_households = campaigns["household_key"].drop_duplicates()

print("\nREDEMPTION HOUSEHOLD VALIDATION:")

print("Unique redeeming households:", len(redemption_households))

print("Redeeming households absent from transactions:", (~redemption_households.isin(purchase_households)).sum())

print("Redeeming households absent from campaign assignments:", (~redemption_households.isin(campaign_households)).sum())

# 9. Validate redemption household-campaign assignments

assignments = pd.read_csv("data/raw/campaign_table.csv", usecols=["household_key", "CAMPAIGN"]).drop_duplicates()

assignment_check = redemptions.merge(
    assignments,
    on=["household_key", "CAMPAIGN"],
    how="left",
    indicator=True,
    validate="many_to_one"
)

unmatched_assignments = (assignment_check["_merge"] == "left_only")

print("\nREDEMPTION CAMPAIGN ASSIGNMENT VALIDATION:")

print("Redemption rows without matching household-campaign assignments:", unmatched_assignments.sum())

print("Distinct unmatched household-campaign pairs:",
      assignment_check.loc[unmatched_assignments, ["household_key", "CAMPAIGN"]].drop_duplicates().shape[0])

# 10. Validate redemption dates against campaign schedules

campaign_dates = pd.read_csv("data/raw/campaign_desc.csv", usecols=["CAMPAIGN", "START_DAY", "END_DAY"])

redemption_timing = redemptions.merge(
    campaign_dates,
    on="CAMPAIGN",
    how="left",
    indicator=True,
    validate="many_to_one"
)

# Check whether campaign schedules were found
missing_schedule = redemption_timing["_merge"] == "left_only"

# Compare redemption days with campaign periods
before_start = (
    (redemption_timing["_merge"] == "both") &
    (redemption_timing["DAY"] < redemption_timing["START_DAY"])
)

after_end = (
    (redemption_timing["_merge"] == "both") &
    (redemption_timing["DAY"] > redemption_timing["END_DAY"])
)

print("\nREDEMPTION DATE VALIDATION:")

print("Redemptions with missing campaign schedules:", missing_schedule.sum())

print("Redemptions before campaign start:", before_start.sum())

print("Redemptions after campaign end:", after_end.sum())