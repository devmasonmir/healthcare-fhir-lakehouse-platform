from src.fhir.parser import FHIRParser
from src.governance.phi_masker import PHIMasker


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


def test_parser_handles_empty_optional_collections():
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "p1",
                    "identifier": [],
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "o1",
                    "subject": {"reference": "Patient/p1"},
                    "code": {"coding": []},
                }
            },
        ],
    }

    parsed = FHIRParser.parse_bundle(bundle)

    assert parsed["patients"][0]["mrn"] is None
    assert parsed["observations"][0]["code"] is None
    assert parsed["observations"][0]["patient_id"] == "p1"


def test_parser_skips_malformed_entries_without_aborting_batch():
    bundle = {
        "entry": [
            None,
            {"resource": None},
            {"resource": "not-an-object"},
            {"resource": {"resourceType": "Patient", "id": "p2"}},
        ]
    }

    parsed = FHIRParser.parse_bundle(bundle)

    assert [patient["patient_id"] for patient in parsed["patients"]] == ["p2"]
    assert parsed["observations"] == []


def test_parser_only_strips_a_leading_patient_reference_prefix():
    bundle = {
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "o2",
                    "subject": {"reference": "Group/Patient/p2"},
                }
            }
        ]
    }

    parsed = FHIRParser.parse_bundle(bundle)

    assert parsed["observations"][0]["patient_id"] == "Group/Patient/p2"


def test_phi_masker():
    raw_pat = {"patient_id": "p1", "mrn": "SECRET_MRN_123"}
    masked = PHIMasker.mask_patient_record(raw_pat)
    assert "mrn" not in masked
    assert len(masked["pseudonymized_patient_key"]) == 16
    assert masked["is_deidentified"] is True
