from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'mason-mir',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'healthcare_fhir_lakehouse_ingestion',
    default_args=default_args,
    description='Automated EHR FHIR ingestion, PHI masking, and dbt transformation',
    schedule_interval='@hourly',
    catchup=False,
) as dag:
    t_parse = BashOperator(task_id='parse_ehr_fhir_bundles', bash_command='echo "Parsing FHIR bundles..."')
    t_mask = BashOperator(task_id='apply_phi_safe_harbor_masking', bash_command='echo "Masking PHI..."')
    t_dbt = BashOperator(task_id='run_clinical_dbt_models', bash_command='cd dbt_project && dbt run')
    t_parse >> t_mask >> t_dbt
