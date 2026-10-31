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

## Finding 4: Discount Values and Floating-Point Precision

### Observation

Three discount columns were investigated:

- RETAIL_DISC
- COUPON_DISC
- COUPON_MATCH_DISC

Nonzero discount amounts are predominantly negative.

### Discount Distribution

| Column | Negative | Zero | Positive |
|---|---:|---:|---:|
| RETAIL_DISC | 1,303,026 | 1,292,670 | 36 |
| COUPON_DISC | 36,422 | 2,559,310 | 0 |
| COUPON_MATCH_DISC | 17,449 | 2,578,283 | 0 |

### Investigation of Positive Retail Discounts

Of the 36 positive RETAIL_DISC values:

- 26 round to zero at two decimal places.
- 10 remain positive after rounding to two decimal places.

The 26 extremely small positive values are consistent with floating-point precision artefacts.

Further investigation identified a relationship between positive retailer discounts and zero-quantity records.

However, the precise amounting meaning of these transactions remains unconfirmed.

### Interpretation

Negative values appear to be the normal convention for recording discounts in this dataset.

Most raw positive retailer discount values are negligible at cent precision.

The remaining 10 positive values require further investigation and should not automatically be classified as errors.

### Data Quality Decision

- Preserve original monetary values in the raw data.
- Use cent-level precision for monetary comparisons.
- Flag meaningful positive retailer discounts.
- Do not automatically reverse discount signs.
- Retain all records unless further evidence supports a cleaning transformation.

### Status

Investigated. No cleaning transformation applied.

## Finding 5: Transaction Time Consistency

### Observation

The transaction dataset contains:

- 711 distinct days (Day 1 to Day 711).
- 102 distinct weeks (Week 1 to Week 102).
- No zero or negative day/week values.

### Investigation

An initial validation assumed that Week 1 contained Days 1-7.

This produced 694,450 mismatched records.

Further investigation of week boundaries showed:

- Week 1: Days 1-5
- Week 2: Days 6-12
- Week 3: Days 13-19

A revised validation formula was applied:

expected_week = ((DAY + 1) // 7) + 1

The revised validation produced zero mismatches across all 2,595,732 transaction records.

### Interpretation

DAY and WEEK_NO are internally consistent under the observed reporting-week convention.

The first reporting week contains only five observed days rather than seven.

### Data Quality Decision

- Retain the original DAY and WEEK_NO columns.
- Use the validated week mapping for time-based analysis.
- Do not assume DAY represents a calendar date.
- No correction is required.
 
### Status

Validated. No cleaning transformation required.

## Finding 6: Transaction Time Validation

### Observation

The TRANS_TIME column records transaction times in HHMM format.

- Minimum time: 0000 (12:00 AM)
- Maximum time: 2359 (11:59 PM)

### Validation

Transaction times were separated into hours and minutes using integer division and modulo.

Validation rules:
- Hours must be between 0 and 23.
- Minutes must be between 0 and 59.

Results: 0 invalid transaction times across 2,595,732 records.

### Interpretation

All recorded transaction times satisfy the expected HHMM format.

This validates the format but does not independently verify the accuracy of each recorded time.

### Data Quality Decision

- Retain the original TRANS_TIME column.
- No cleaning transformation is required.
- Derive hour-based variables when needed for future customer behaviour analysis.

### Status

Validated. No cleaning transformation required.

## Finding 7: Product Referential Integrity

### Objective

Validate the relationship between transaction_data.csv and product.csv using PRODUCT_ID.

### Validation Results

- Duplicate PRODUCT_ID values in product.csv: 0
- Transaction rows with unmatched PRODUCT_ID: 0
- Distinct unmatched PRODUCT__ID values: 0

### Interpretation

All transaction product IDs have corresponding records in the product catalogue.

PRODUCT_ID is unique in product.csv, supporting a many-to-one relationship between transaction records and product information.

These findings indicate that joining the tables on PRODUCT_ID should not introduce unmatched records or duplicate transaction rows.

### Data Quality Decision

- Retain all product IDs.
- No correction or imputation is required.
- Use PRODUCT_ID as the join key for transaction and product analysis.
- Validate row counts after performing joins.

### Status

Validated. No cleaning transformation required.
