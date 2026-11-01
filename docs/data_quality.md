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

## Finding 8: Household Demographic Coverage

### Objective

Assess the availability and uniqueness of household demographic information.

### Validation Results

- Unique purchasing households: 2,500
- Households with demographic records: 801
- Duplicate demographic household IDs: 0
- Purchasing households without demographics: 1,699
- Demographic coverage: 32.04%

### Interpretation

Demographic information is available for only 32.04% of purchasing households.

All 801 demographic household IDs correspond to households in the transaction dataset.

The demographic subset may not be representative of the full purchasing population.

### Data Quality Decision

- Retain all 2,500 purchasing households.
- Do not impute missing demographic categories without a justified methodology.
- Use LEFT JOIN when demographic enrichment should preserve all transaction records.
- Restrict demographic analyses to households with available information.
- Clearly report sample sizes and limitations.

### Status

Validated. Demographic coverage limitation documented. No records removed.

## Finding 9: Shopping Basket Consistency

### Objective

Validate whether BASKET_ID consistently identifies a single shopping event.

### Validation Results

- Total unique baskets: 276,484
- Baskets associated with multiple households: 0
- Baskets associated with multiple days: 0
- Baskets associated with multiple stores: 0
- Baskets associated with multiple checkout times: 0

### Interpretation

Each basket ID is associated with exactly one household, day, store, and recorded checkout time.

These findings support using BASKET_ID as the identifier for individual shopping events.

### Data Quality Decision

- Retain all basket IDs.
- Use BASKET_ID to aggregate product-line transactions into basket-level records.
- Count distinct BASKET_ID values when calculating shopping frequency.
- Validate basket-level sales aggregations before calculating business KPIs.
- Consider special transaction types when interpreting basket-level metrics.

### Status

Validated. No cleaning transformation required.

## Finding 10: Campaign Household Referential Integrity

### Objective

Validate the relationship between campaign_table.csv and transaction_data.csv using household_key.

### Validation Results

- Total purchasing households: 2,500
- Households assigned to campaigns: 1,584
- Campaign households absent from transactions: 0
- Purchasing households without campaign assignments: 916
- Purchasing household campaign coverage: 63.36%

### Interpretation

All households assigned to marketing campaigns have corresponding transaction records.

916 purchasing households have no recorded campaign assignment.

The dataset supports linking campaign assignments with household purchasing behaviour.

However, assignment does not establish actual campaign exposure or campaign-driven purchases.

### Data Quality Decision

- Retain all household records.
- Preserve households without campaign assignments.
- Use household-key to link campaign assignments with purchasing activity.
- Do not automatically treat unassigned households as a randomised control group.
- Account for potential selection bias when evaluating campaign effectiveness.

### Status

Validated. No cleaning transformation required.

## Finding 11: Campaign Schedule Validation

### Objective

Validate campaign schedule consistency and assess coverage relative to the transaction observation period.

### Validation Results

- Total campaigns: 30
- Duplicate campaign IDs: 0
- Campaigns starting after their end day: 0
- Last observed transaction day: 711
- Campaigns ending after transaction coverage: 1

### Interpretation

Campaign IDs are unique, and no campaign has a start day later than its end day.

Campaign 24 runs from Day 659 to Day 719, but transaction records are available only through Day 711.

The final eight days of Campaign 24 fall outside the observed transaction period.

This is an observation coverage limitation rather than necessarily an invalid campaign schedule.

### Data Quality Decision

- Retain all campaign records.
- Preserve original START_DAY and END_DAY values.
- Flag campaigns extending beyond transaction coverage.
- Do not interpret unobserved days as zero sales.
- Account for incomplete observation windows when comparing campaign performance.
- Use comparable observation periods where appropriate.

### Status

Validated. One campaign has incomplete transaction coverage. No records removed.

## Finding 12: Campaign Referential Integrity

### Objective

Validate the relationship between campaign_table.csv and campaign_desc.csv using CAMPAIGN.

### Validation Results

- Total campaign assignment records: 7,208
- Unique campaign IDs: 30
- Duplicate campaign IDs in campaign_desc.csv: 0
- Assignment rows with unmatched campaigns: 0
- Distinct unmatched campaign IDs: 0
- Assignment rows with mismatched campaign types: 0

### Interpretation

All campaign assignments reference valid campaign IDs.

Campaign descriptions are consistent across the assignment and campaign description datasets.

The relationship between campaign assignments and campaign descriptions is many-to-one.

### Data Quality Decision

- Retain all campaign assignment records.
- Use CAMPAIGN as the join key.
- Preserve the 7,208 assignment records when enriching them with campaign descriptions.
- Validate row counts after joining the tables.
- No campaign ID or description corrections required.

### Status

Validated. No cleaning transformation required.

## Finding 13: Duplicate Coupon Eligibility Records

### Objective

Investigate repeated coupon-product-campaign combinations in coupon.csv and assess their potential impact on downstream analysis.

### Validation Results

- Total coupon records: 124,548
- Unique coupon IDs: 1,135
- Unique products: 44,133
- Unique campaigns: 30
- Additional duplicate combinations: 5,164
- Distinct combinations repeated: 1,824
- Maximum occurrences of one combination: 19
- Overall duplicate rate: 4.15%
- Unique coupon-product-campaign combinations: 119,384

### Campaign-Level Findings

Duplication is concentrated in eight campaigns.

- Campaign 27: 3,391 extra rows (78.46%)
- Campaign 30: 576 extra rows (14.03%)
- Campaign 26: 292 extra rows (7.80%)
- Campaign 8: 608 extra rows (3.17%)

Campaign 27 has the highest duplicate count and rate.

### Interpretation

The coupon dataset contains repeated identical coupon-product-campaign relationships.

These repetitions could inflate relationship counts and multiply records during joins.

The underlying cause of the repetitions has not been established.

### Data Quality Decision

- Preserve the original coupon.csv unchanged.
- Create a distinct coupon-product-campaign eligibility table for relationship-based analysis.
- Retain one record per unique combination of COUPON_UPC, PRODUCT_ID, and CAMPAIGN.
- Do not interpret repeated rows as additional coupons, products, or redemptions.
- Preserve duplicate counts for auditing.
- Validate row counts after downstream joins.

### Status

Duplicate patterns investigated.
Analytical deduplication recommended.
No raw records removed.

## Finding 14: Coupon Redemption Referential Integrity

### Objective

Validate recorded coupon redemptions against coupon-campaign relationships in coupon.csv.

### Validation Results

- Total redemption records: 2,318
- Unique redeeming households: 434
- Unique redeemed coupon IDs: 556
- Unique campaigns represented: 30
- Exact duplicate redemption records: 0
- Redemption rows with unmatched coupon-campaign pairs: 0
- Distinct unmatched coupon-campaign pairs: 0

### Interpretation

All recorded coupon redemptions reference valid coupon-campaign combinations in coupon.csv.

Coupon eligibility data contains multiple product records per coupon. Distinct coupon-campaign pairs were therefore used for referential validation.

No unmatched coupon-campaign relationships were found.

### Data Quality Decision

- Preserve all redemption records.
- Retain the original redemption dataset unchanged.
- Use COUPON_UPC and CAMPAIGN together to validate redemption-to-eligibility relationships.
- Deduplicate the coupon-campaign lookup before joins.
- Avoid multiplying redemption counts when joining to product-level coupon eligibility data.
- Do not assume that eligibility establishes actual household-level coupon exposure.

### Status

Validated. No cleaning transformation required.
