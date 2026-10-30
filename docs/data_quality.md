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
