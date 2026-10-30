# Data Quality Assessment

## Dataset
transaction_data.csv

## Initial Assessment

- Total records: 2,595,732
- Total columns: 12
- Missing values: 0
- Exact duplicate rows: 0

## Finding 1: Extreme Quantity Values

### Observation

The QUANTITY column contains unusually large values.

- Mean quantity: 100.43
- Median quantity: 1
- Maximum quantity: 89,638

### Investigation

The largest quantities were associated with products classified as GASOLINE-REG UNLEADED.

Two identified product IDs:
- 6534178
- 6544236

Further analysis identified 24,962 transaction records belonging to this gasoline sub-category.

Excluding these records:

- Mean quantity: 1.30
- Maximum quantity: 144

### Interpretation

Gasoline transactions appear to use a different quantity measurement scale from ordinary grocery items.

The exact measurement unit has not been confirmed.

Combining gasoline quantities with grocery unit counts makes aggregate quantity statistics difficult to interpret.

### Data Quality Decision

No records will be deleted based solely on extreme quantities.

Gasoline transactions will be retained in the source data and handled separately when calculating metrics that require comparable physical units.

Further validation may be required before calculating quantity-based metrics.

### Status

Investigated. No cleaning transformation applied.

## Finding 2: Zero Quantity with Positive Sales

### Observation

The transaction dataset contains:

- 14,399 records with zero quantity and zero sales.
- 67 records with zero quantity and positive sales.
- 4,451 records with positive quantity and zero sales.

### Investigation

Of the 67 zero-quantity records with positive sales:

- 29 have extremely small positive sales values below 0.0000001, consistent with floating-point precision artefacts.
- 38 have positive sales values after rounding to two decimal places.

The 38 records are distributed across:

- Produce: 17
- Drug GM: 11
- Grocery: 7
- Deli: 2
- Meat: 1

The highest observed sales value among these records is $5.82, associated with a grapes product.

### Interpretation

Some zero-quantity records may reflect product measurement conventions, particularly for weighted produce.

However, these records also occur in non-produce departments.

The exact causes cannot be established from the available evidence.

### Data Quality Decision

- Retain the original transaction records.
- Flag zero-quantity records with positive sales for analytical considerations.
- Exclude zero-quantity records from calculations requiring division by quantity.
- Do not automatically exclude these records from revenue calculations.
- Investigate zero-sales transactions seperately.

### Status

Investigated. No cleaning transformation applied.

## Finding 3: Positive Quantity with Zero Sales

### Observation

4,451 transaction records have positive quantities but zero sales values.

### Discount Investigation

Of these records:

- 3,748 have negative retailer discounts.
- 43 have nonzero manufacturer coupon discounts.
- 702 have no recorded discounts.

These categories are not mutually exclusive.

### Investigation of Records Without Discounts

Among the 702 records without recorded discounts:

- 444 belong to the COUP/STR & MFG department.
- 231 belong to GROCERY.
- The remaining 27 belong to other departments.

Of the 231 grocery records, 225 belong to BAG SNACKS.

### Snack Product Investigation

The 225 zero-sales snack records involve 18 distinct products.

All 18 products also appear in positive-sales transactions, with 1,132 positive-sales transaction lines in total.

### Interpretation

The coupon-related entries appear to represent a different transaction type from ordinary merchandise purchases.

Zero-sales snack transactions occur for products that are also sold for positive amounts.

The cause of these zero-sales transactions cannot be established from the available data.

### Data Quality Decision

- Retain all records at this stage.
- Flag zero-sales transactions for analytical consideration.
- Distinguish coupon-related entries from physical merchandise when calculating item counts.
- Do not classify zero-sales snack records as promotional giveaways without further evidence.
- Preserve recorded sales values rather than imputing prices.

### Status

Investigated. No cleaning transformation applied.
