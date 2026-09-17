import pytest
import json
from src.fhir.parser import FHIRParser
from src.governance.phi_masker import PHIMasker
from src.quality.data_contracts import ClinicalDataContractValidator

def test_fhir_bundle_parser():
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Patient", "id": "p1", "gender": "male"}},
            {"resource": {"resourceType": "Observation", "id": "o1", "code": {"coding": [{"code": "8867-4"}]}}}
        ]
    }
    parsed = FHIRParser.parse_bundle(bundle)
    assert len(parsed["patients"]) == 1
    assert len(parsed["observations"]) == 1

def test_phi_masker():
    raw_pat = {"patient_id": "p1", "mrn": "SECRET_MRN_123"}
    masked = PHIMasker.mask_patient_record(raw_pat)
    assert "mrn" not in masked
    assert len(masked["pseudonymized_patient_key"]) == 16
    assert masked["is_deidentified"] is True
