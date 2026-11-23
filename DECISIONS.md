# Implementation decisions

## Match amounts against A's `total_value`

B describes the full event amount, so the comparison uses A's adjusted total. Comparing with `base_value` would miss adjustments.

## Keep original values when parsing fails

Each source row is retained. The parsed field becomes null when the value is blank or invalid, while its raw text remains available for inspection. Treating a blank as zero would invent financial data.

## Normalize reference formatting before matching

Reference prefixes, spaces, and punctuation vary across the exports. The importer derives a stable normalized reference from the digits so values such as `rec1034`, ` REC - 1070 `, and `1112` can match their records.

## Accept a repeated reference only when the entries form a valid split

Several B entries are treated as a split if their combined amount equals A's total. Otherwise, repeated references are reported for review. This keeps the valid split for REC-1055 while flagging the duplicate full amount for REC-1042.

## Keep VOIDED A records in the comparison

The source does not specify that a void removes a corresponding B entry. The application therefore leaves the record visible for reconciliation instead of silently suppressing it.

## Compare dates and locations as well as amounts

A matching amount alone does not establish that both systems describe the same event. Date and location differences are reported as their own review reasons.

## Use the location file to scope records

`locations.csv` is the ownership mapping. A matched record is associated with its A location; an orphan is associated with its B location. If the B location belongs to another organization, the API does not disclose that foreign location ID.

## Use SQLite with decimal amounts

SQLite keeps the project self-contained, while decimal arithmetic avoids floating-point rounding in monetary comparisons. The Vercel build prepares the database before the function runs; the deployed function reads that preloaded copy.
