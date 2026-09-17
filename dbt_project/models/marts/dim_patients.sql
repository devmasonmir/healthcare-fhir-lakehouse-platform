SELECT
    pseudonymized_patient_key,
    gender,
    birth_date,
    is_deidentified,
    CURRENT_TIMESTAMP() AS loaded_at
FROM {{ ref('stg_fhir_patients') }}
