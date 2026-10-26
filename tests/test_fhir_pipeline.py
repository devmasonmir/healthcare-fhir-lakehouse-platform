import os
from unittest.mock import patch

import pytest

from src.fhir.parser import FHIRParser
from src.governance.phi_masker import PHIMasker


TEST_KEY = "synthetic-test-key-that-is-at-least-32-bytes"


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


def test_phi_masker_removes_mrn_without_mutating_source():
    raw_patient = {"patient_id": "p1", "mrn": "SYNTHETIC_MRN_123"}

    masked = PHIMasker.mask_patient_record(raw_patient, TEST_KEY)

    assert raw_patient["mrn"] == "SYNTHETIC_MRN_123"
    assert "mrn" not in masked
    assert len(masked["pseudonymized_patient_key"]) == 32
    assert masked["is_mrn_pseudonymized"] is True


def test_phi_masker_is_deterministic_per_key_and_separates_keys():
    first = PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123", TEST_KEY)
    repeated = PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123", TEST_KEY)
    different_key = PHIMasker.pseudonymize_mrn(
        "SYNTHETIC_MRN_123",
        "different-synthetic-key-that-is-32-bytes",
    )

    assert first == repeated
    assert first != different_key


def test_phi_masker_reads_key_from_environment():
    with patch.dict(os.environ, {PHIMasker.KEY_ENV_VAR: TEST_KEY}, clear=True):
        assert PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123")


@pytest.mark.parametrize("key", [None, "too-short"])
def test_phi_masker_rejects_missing_or_short_keys(key):
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123", key)


def test_phi_masker_rejects_non_string_identifiers():
    with pytest.raises(TypeError):
        PHIMasker.pseudonymize_mrn(12345, TEST_KEY)
