from pathlib import Path
import pandas as pd

# Read the first five rows
df = pd.read_csv("data/raw/transaction_data.csv", nrows=5)

# Display the column names
print("COLUMN NAMES:")
print(df.columns.tolist())

# Display the first five rows
print("\nFIRST FIVE ROWS:")
print(df.to_string(index=False))