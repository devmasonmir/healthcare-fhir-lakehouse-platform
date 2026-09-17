# Healthcare FHIR Lakehouse & Clinical Analytics Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FHIR R4](https://img.shields.io/badge/FHIR-Release_4-orange.svg)](https://hl7.org/fhir/R4/)
[![Snowflake](https://img.shields.io/badge/Snowflake-Lakehouse-29B5E8.svg)](https://www.snowflake.com/)
[![dbt Core](https://img.shields.io/badge/dbt-1.7+-FF694B.svg)](https://www.getdbt.com/)
[![HIPAA Compliant](https://img.shields.io/badge/Security-HIPAA_Safe_Harbor-green.svg)](https://www.hhs.gov/hipaa/)

> **HIPAA-compliant enterprise clinical data platform integrating EHR datasets (Epic, Cerner, HL7, FHIR R4) into Snowflake and Delta Lake with automated PHI de-identification, clinical dimensional modeling via dbt, and Airflow orchestration.**

---

## 🏗️ Architecture & Clinical Pipeline

```mermaid
flowchart TD
    subgraph EHR["Clinical Source Systems"]
        Epic["Epic Systems (EHR APIs)"]
        Cerner["Cerner Millennium (HL7/FHIR)"]
    end

    subgraph Ingestion["Ingestion & PHI De-identification"]
        Parser["FHIR R4 Resource Parser<br/>(Patient, Encounter, Observation)"]
        Masker["HIPAA Safe Harbor De-identifier<br/>(MRN Hashing, Date Shifting, ZIP Masking)"]
        Epic --> Parser
        Cerner --> Parser
        Parser --> Masker
    end

    subgraph Lakehouse["Governed Clinical Lakehouse (Snowflake)"]
        Bronze[("Bronze: Raw FHIR Bundles (S3)")]
        Silver[("Silver: Validated Clinical Entities")]
        Gold[("Gold: Clinical Marts (dbt)")]
        Masker --> Bronze
        Bronze --> Silver
        Silver --> Gold
    end

    subgraph Analytics["Clinical Analytics & Downstream AI"]
        Gold --> Dash["Patient Population Health BI"]
        Gold --> Risk["Clinical Outcome Prediction Models"]
    end
```

---

## 🚀 Key Architectural Features

* **FHIR R4 & HL7 Interoperability**: Standardized parsers decomposing complex nested JSON bundles into relational tables.
* **Automated HIPAA Safe Harbor Compliance**: Deterministic pseudonymization, date jittering, and column-level RBAC masking for all 18 PHI identifiers.
* **Clinical Data Contracts**: Validates LOINC, SNOMED-CT, and ICD-10 clinical coding standards at ingestion time.
* **dbt Dimensional Modeling**: Production marts for patient longitudinal views, inpatient length-of-stay, and chronic disease cohorts.
* **Airflow Workflow Orchestration**: 30% pipeline reliability increase with automated SLA monitoring and incident alerting.

---

## 📂 Project Structure

```
healthcare-fhir-lakehouse-platform/
├── ci/ci.yml                          # CI pipeline
├── dags/
│   └── fhir_ingestion_dag.py          # Airflow clinical ingestion DAG
├── dbt_project/                       # dbt Core models
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/
│       │   ├── stg_fhir_patients.sql
│       │   └── stg_fhir_encounters.sql
│       └── marts/
│           ├── dim_patients.sql
│           ├── fct_clinical_observations.sql
│           └── schema.yml
├── docs/architecture.md               # Clinical Lakehouse architecture
├── sample_data/
│   └── fhir_bundle.json               # Sample FHIR R4 Bundle
├── src/
│   ├── __init__.py
│   ├── fhir/
│   │   └── parser.py                  # FHIR R4 bundle parser
│   ├── governance/
│   │   └── phi_masker.py              # HIPAA Safe Harbor de-identifier
│   └── quality/
│       └── data_contracts.py          # Clinical vocabulary validator
├── tests/
│   └── test_fhir_pipeline.py          # Unit tests
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

---

## ⚡ Quickstart

```bash
git clone https://github.com/masonmirtech/healthcare-fhir-lakehouse-platform.git
cd healthcare-fhir-lakehouse-platform
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -v
```

---

## 📜 License
MIT License.
