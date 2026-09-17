# Healthcare FHIR Lakehouse Platform Architecture

## Compliance & Security
1. **HIPAA Safe Harbor**: All direct patient identifiers (Name, SSN, MRN, Address) are pseudonymized via HMAC-SHA256 before writing to Silver tables.
2. **Clinical Standards**: FHIR R4 resource definitions map cleanly into Kimball dimensional star schemas.
