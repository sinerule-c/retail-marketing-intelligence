import pandas as pd

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