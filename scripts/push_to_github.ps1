param([string]$Username = "masonmirtech")
git init; git branch -M main; git add .
git commit -m "feat: Healthcare FHIR Lakehouse & Clinical Analytics Platform - FHIR R4, Snowflake, dbt Core, HIPAA De-identification"
git remote remove origin 2>$null
git remote add origin "https://github.com/$Username/healthcare-fhir-lakehouse-platform.git"
git push -u origin main
