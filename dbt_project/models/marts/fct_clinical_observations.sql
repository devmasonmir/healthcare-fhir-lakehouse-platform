SELECT
    obs_id,
    pseudonymized_patient_key,
    code AS loinc_code,
    value AS observation_value,
    unit,
    recorded_time
FROM {{ source('clinical_silver', 'raw_observations') }}
