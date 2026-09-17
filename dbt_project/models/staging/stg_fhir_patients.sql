SELECT
    pseudonymized_patient_key,
    gender,
    birth_date,
    is_deidentified
FROM {{ source('clinical_silver', 'raw_patients') }}
WHERE pseudonymized_patient_key IS NOT NULL
