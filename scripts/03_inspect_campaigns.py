import pandas as pd

# Load household campaign assignments
campaigns = pd.read_csv("data/raw/campaign_table.csv")

print("DATASET DIMENSIONS:")
print(campaigns.shape)

print("\nCOLUMN NAMES:")
print(campaigns.columns.tolist())

print("\nFIRST 10 ROWS:")
print(campaigns.head(10).to_string(index=False))

print("\nDATA TYPES:")
print(campaigns.dtypes)

# Check campaign assignment granularity

print("\nCAMPAIGN ASSIGNMENT SUMMARY:")

print("Unique households:", campaigns["household_key"].nunique())

print("Unique campaigns:", campaigns["CAMPAIGN"].nunique())

print("Duplicate household-campaign pairs:", campaigns.duplicated(subset=["household_key", "CAMPAIGN"]).sum())

# Validate household IDs across datasets

transactions = pd.read_csv("data/raw/transaction_data.csv", usecols=["household_key"])

purchase_ids = transactions["household_key"].unique()
campaign_ids = campaigns["household_key"].unique()

print("\nCAMPAIGN HOUSEHOLD VALIDATION:")

print("Campaign households absent from transactions:", (~pd.Series(campaign_ids).isin(purchase_ids)).sum())

print("Purchasing households without campaign assignments:", (~pd.Series(purchase_ids).isin(campaign_ids)).sum())

# Inspect campaigm descriptions and timing

campaign_desc = pd.read_csv("data/raw/campaign_desc.csv")

print("\nCAMPAIGN DESCRIPTION DATASET:")

print("Dataset dimensions:", campaign_desc.shape)

print("\nColumn names:")
print(campaign_desc.columns.tolist())

print("\nFirst 10 rows:")
print(campaign_desc.head(10).to_string(index=False))

print("\nData types:")
print(campaign_desc.dtypes)

# Validate campaign schedules

print("\nCAMPAIGN SCHEDULE VALIDATION:")

print("Duplicate campaign IDs:", campaign_desc["CAMPAIGN"].duplicated().sum())

print("Campaigns starting after their end day", (campaign_desc["START_DAY"] > campaign_desc["END_DAY"]).sum())

# Compare campaign schedules with transaction coverage
last_transaction_day = pd.read_csv("data/raw/transaction_data.csv", usecols=["DAY"])["DAY"].max()

print("Last observed transaction day:", last_transaction_day)

print("Campaigns ending after transaction coverage:", (campaign_desc["END_DAY"] > last_transaction_day).sum())

# Validate campaign relationships across tables

campaign_check = campaigns.merge(
    campaign_desc[["CAMPAIGN", "DESCRIPTION"]],
    on="CAMPAIGN",
    how="left",
    suffixes=("_assignment", "_schedule"),
    indicator=True,
    validate="many_to_one"
)

# Check unmatched campaign IDs
unmatched = campaign_check["_merge"] == "left_only"

# Compare campaign descriptions for matched IDs
type_mismatch = (
    (campaign_check["_merge"] == "both") &
    (campaign_check["DESCRIPTION_assignment"] != campaign_check["DESCRIPTION_schedule"])
)

print("\nCAMPAIGN REFERENTIAL INTEGRITY:")

print("Assignment rows with unmatched campaigns:", unmatched.sum())

print("Distinct unmatched campaign IDs:", campaign_check.loc[unmatched, "CAMPAIGN"].nunique())

print("Assignment rows with mismatched campaign types:", type_mismatch.sum())