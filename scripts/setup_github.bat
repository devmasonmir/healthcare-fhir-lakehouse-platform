@echo off
setlocal
echo ===================================================
echo  Healthcare FHIR Lakehouse Platform
echo ===================================================
git init
git branch -M main
git add .
git commit -m "feat: Healthcare FHIR Lakehouse & Clinical Analytics Platform - FHIR R4, Snowflake, dbt Core, HIPAA De-identification"
set /p GH_USER="Enter GitHub username (or press enter for soniablaketech/masonmirtech): "
git remote remove origin 2>nul
git remote add origin https://github.com/%GH_USER%/healthcare-fhir-lakehouse-platform.git
git push -u origin main
pause
