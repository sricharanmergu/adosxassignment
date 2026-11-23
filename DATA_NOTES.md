# Source data observations

- **Locations:** 5 data rows; 3 location IDs belong to ORG-A and 2 belong to ORG-B.
- **System A:** 120 records. The export has one blank `actor_id` and a VOIDED record (REC-1019).
- **System B:** 121 entries. Three references use unusual formatting (`rec1034`, ` REC - 1070 `, and `1112`); one amount is blank and one uses comma grouping (`1,25,400.00`).
- B includes an unmatched reference (REC-1999), a repeated reference (REC-1042), and a second-part entry for REC-1055. A record with reference REC-1015 has no B entry.
- Some matched records differ by date or location. At least one match crosses organization locations, so the API must filter foreign location details.
- The importer keeps every B row. The CSV files in `backend/data/` are the original supplied inputs.

These counts describe source entries. The web table shows reconciliation exceptions after organization and reason filters are applied, not every imported row.
