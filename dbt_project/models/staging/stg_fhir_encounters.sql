SELECT
    encounter_id,
    pseudonymized_patient_key,
    encounter_class,
    start_time,
    end_time
FROM {{ source('clinical_silver', 'raw_encounters') }}
