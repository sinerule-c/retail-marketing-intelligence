import pandas as pd

# Inspect only the first 10 rows of the large dataset
causal_sample = pd.read_csv("data/raw/causal_data.csv", nrows=10)

print("\nCAUSAL DATASET INSPECTION:")

print("\nColumn names:")
print(causal_sample.columns.tolist())

print("\nFirst 10 rows:")
print(causal_sample.to_string(index=False))

print("\nSample data types:")
print(causal_sample.dtypes)

# 2. Inspect promotional codes using chunks

total_rows = 0

display_codes = set()
mailer_codes = set()

for chunk in pd.read_csv(
    "data/raw/causal_data.csv",
    usecols=["display", "mailer"],
    dtype={"display": "string", "mailer": "string"},
    chunksize=100_000
):
    total_rows += len(chunk)

    display_codes.update(
        chunk["display"].dropna().unique()
    )

    mailer_codes.update(
        chunk["mailer"].dropna().unique()
    )

print("\nPROMOTIONAL CODE SUMMARY:")

print("Total dataset rows:", total_rows)

print("Unique display codes:", sorted(display_codes))

print("Unique mailer codes:", sorted(mailer_codes))

# 3. Count promotional code frequencies

from collections import Counter

display_counts = Counter()
mailer_counts = Counter()

for chunk in pd.read_csv(
    "data/raw/causal_data.csv",
    usecols=["display", "mailer"],
    dtype={"display": "string", "mailer": "string"},
    chunksize=100_000
):
    display_counts.update(
        chunk["display"].fillna("MISSING").value_counts().to_dict()
    )

    mailer_counts.update(
        chunk["mailer"].fillna("MISSING").value_counts().to_dict()
    )

print("\nDISPLAY CODE FREQUENCIES:")
print(pd.Series(display_counts).sort_values(ascending=False).to_string())

print("\nMAILER CODE FREQUENCIES:")
print(pd.Series(mailer_counts).sort_values(ascending=False).to_string())

# 4. Validate promotional data identifiers and weeks

key_columns = ["PRODUCT_ID", "STORE_ID", "WEEK_NO"]

missing_counts = {
    "PRODUCT_ID": 0,
    "STORE_ID": 0,
    "WEEK_NO": 0
}

observed_weeks = set()

for chunk in pd.read_csv(
    "data/raw/causal_data.csv",
    usecols=key_columns,
    chunksize=100_000
):
    for column in key_columns:
        missing_counts[column] += chunk[column].isna().sum()

    observed_weeks.update(
        chunk["WEEK_NO"].dropna().unique()
    )

print("\nPROMOTIONAL DATA KEY VALIDATION:")

print("Missing product IDs:", missing_counts["PRODUCT_ID"])
print("Missing store IDs:", missing_counts["STORE_ID"])
print("Missing week numbers:", missing_counts["WEEK_NO"])

print("Unique weeks:", len(observed_weeks))
print("Minimum week:", min(observed_weeks))
print("Maximum week:", max(observed_weeks))

# 5. Check uniqueness of product-store-week combinations

import sqlite3

total_rows = 0

with sqlite3.connect("data/causal_key_check.sqlite") as conn:

    conn.execute("DROP TABLE IF EXISTS promo_keys")

    conn.execute("""
        CREATE TABLE promo_keys (
            PRODUCT_ID INTEGER,
            STORE_ID INTEGER,
            WEEK_NO INTEGER,
            PRIMARY KEY (PRODUCT_ID, STORE_ID, WEEK_NO)
        ) WITHOUT ROWID
    """)

    for chunk in pd.read_csv(
        "data/raw/causal_data.csv",
        usecols=["PRODUCT_ID", "STORE_ID", "WEEK_NO"],
        chunksize=100_000
    ):
        total_rows += len(chunk)

        conn.executemany(
            "INSERT OR IGNORE INTO promo_keys VALUES (?, ?, ?)",
            chunk.itertuples(index=False, name=None)
        )

    unique_keys = conn.execute(
        "SELECT COUNT(*) FROM promo_keys"
    ).fetchone()[0]

print("\nPROMOTIONAL KEY UNIQUENESS:")

print("Total records:", total_rows)
print("Unique product-store-week combinations:", unique_keys)
print("Extra duplicate combinations:", total_rows - unique_keys)


# 6. Check exact duplicate promotional records

total_full_rows = 0

with sqlite3.connect("data/causal_full_row_check.sqlite") as conn:

    conn.execute("DROP TABLE IF EXISTS promo_full_rows")

    conn.execute("""
        CREATE TABLE promo_full_rows (
            PRODUCT_ID INTEGER,
            STORE_ID INTEGER,
            WEEK_NO INTEGER,
            display TEXT,
            mailer TEXT,
            PRIMARY KEY (
                PRODUCT_ID, STORE_ID, WEEK_NO, display, mailer
            )
        ) WITHOUT ROWID
    """)

    for chunk in pd.read_csv(
        "data/raw/causal_data.csv",
        dtype={"display": "string", "mailer": "string"},
        chunksize=100_000
    ):
        total_full_rows += len(chunk)

        conn.executemany(
            "INSERT OR IGNORE INTO promo_full_rows VALUES (?, ?, ?, ?, ?)",
            chunk.itertuples(index=False, name=None)
        )

    unique_full_rows = conn.execute(
        "SELECT COUNT(*) FROM promo_full_rows"
    ).fetchone()[0]

print("\nPROMOTIONAL RECORD DUPLICATE ANALYSIS:")

print("Total records:", total_full_rows)

print("Unique full records:", unique_full_rows)

print("Exact duplicate rows:", total_full_rows - unique_full_rows)

print("Additional distinct code combinations for repeated keys:", unique_full_rows - unique_keys)


# 7. Examine product-store-week groups with multiple codes

with sqlite3.connect("data/causal_full_row_check.sqlite") as conn:

    examples = pd.read_sql_query("""
        SELECT
            PRODUCT_ID,
            STORE_ID,
            WEEK_NO,
            COUNT(*) AS code_combinations,
            GROUP_CONCAT(
                '(' || display || ', ' || mailer || ')',
                ' | '
            ) AS display_mailer_pairs

        FROM promo_full_rows

        GROUP BY PRODUCT_ID, STORE_ID, WEEK_NO

        HAVING COUNT(*) > 1

        LIMIT 10
    """, conn)

print("\nMULTIPLE PROMOTIONAL CODES EXAMPLES:")
print(examples.to_string(index=False))


# 8. Classify promotional code differences

with sqlite3.connect("data/causal_full_row_check.sqlite") as conn:

    result = pd.read_sql_query("""
        WITH repeated_keys AS (
            SELECT
                PRODUCT_ID,
                STORE_ID,
                WEEK_NO,
                MIN(display) AS min_display,
                MAX(display) AS max_display,
                MIN(mailer) AS min_mailer,
                MAX(mailer) AS max_mailer
            FROM promo_full_rows
            GROUP BY PRODUCT_ID, STORE_ID, WEEK_NO
            HAVING COUNT(*) > 1
        )

        SELECT
            COUNT(*) AS repeated_key_groups,

            SUM(CASE
                WHEN min_display != max_display
                 AND min_mailer = max_mailer
                THEN 1 ELSE 0
            END) AS display_only,

            SUM(CASE
                WHEN min_display = max_display
                 AND min_mailer != max_mailer
                THEN 1 ELSE 0
            END) AS mailer_only,

            SUM(CASE
                WHEN min_display != max_display
                 AND min_mailer != max_mailer
                THEN 1 ELSE 0
            END) AS both_differ

        FROM repeated_keys
    """, conn)

print("\nPROMOTIONAL CODE DIFFERENCE SUMMARY:")
print(result.to_string(index=False))