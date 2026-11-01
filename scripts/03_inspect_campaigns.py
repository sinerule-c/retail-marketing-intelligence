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