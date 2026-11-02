import copy
import os
import unittest
from unittest.mock import patch

from src.fhir.parser import FHIRParser
from src.governance.phi_masker import PHIMasker
from src.quality.data_contracts import ClinicalDataContractValidator


TEST_KEY = "synthetic-test-key-that-is-at-least-32-bytes"


class FHIRParserTests(unittest.TestCase):
    def test_fhir_bundle_parser(self):
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "p1",
                        "gender": "male",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "o1",
                        "code": {"coding": [{"code": "8867-4"}]},
                    }
                },
            ],
        }

        parsed = FHIRParser.parse_bundle(bundle)

        self.assertEqual(len(parsed["patients"]), 1)
        self.assertEqual(len(parsed["observations"]), 1)

    def test_parser_handles_empty_optional_collections(self):
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

        self.assertIsNone(parsed["patients"][0]["mrn"])
        self.assertIsNone(parsed["observations"][0]["code"])
        self.assertEqual(parsed["observations"][0]["patient_id"], "p1")

    def test_parser_skips_malformed_entries_without_aborting_batch(self):
        bundle = {
            "entry": [
                None,
                {"resource": None},
                {"resource": "not-an-object"},
                {"resource": {"resourceType": "Patient", "id": "p2"}},
            ]
        }

        parsed = FHIRParser.parse_bundle(bundle)

        self.assertEqual(
            [patient["patient_id"] for patient in parsed["patients"]],
            ["p2"],
        )
        self.assertEqual(parsed["observations"], [])

    def test_parser_only_strips_a_leading_patient_reference_prefix(self):
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

        self.assertEqual(
            parsed["observations"][0]["patient_id"],
            "Group/Patient/p2",
        )


class PHIMaskerTests(unittest.TestCase):
    def test_phi_masker_removes_mrn_without_mutating_source(self):
        raw_patient = {"patient_id": "p1", "mrn": "SYNTHETIC_MRN_123"}

        masked = PHIMasker.mask_patient_record(raw_patient, TEST_KEY)

        self.assertEqual(raw_patient["mrn"], "SYNTHETIC_MRN_123")
        self.assertNotIn("mrn", masked)
        self.assertEqual(len(masked["pseudonymized_patient_key"]), 32)
        self.assertIs(masked["is_mrn_pseudonymized"], True)

    def test_phi_masker_is_deterministic_per_key_and_separates_keys(self):
        first = PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123", TEST_KEY)
        repeated = PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123", TEST_KEY)
        different_key = PHIMasker.pseudonymize_mrn(
            "SYNTHETIC_MRN_123",
            "different-synthetic-key-that-is-32-bytes",
        )

        self.assertEqual(first, repeated)
        self.assertNotEqual(first, different_key)

    def test_phi_masker_reads_key_from_environment(self):
        with patch.dict(os.environ, {PHIMasker.KEY_ENV_VAR: TEST_KEY}, clear=True):
            self.assertTrue(PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123"))

    def test_phi_masker_rejects_missing_or_short_keys(self):
        with patch.dict(os.environ, {}, clear=True):
            for key in (None, "too-short"):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    PHIMasker.pseudonymize_mrn("SYNTHETIC_MRN_123", key)

    def test_phi_masker_rejects_non_string_identifiers(self):
        with self.assertRaises(TypeError):
            PHIMasker.pseudonymize_mrn(12345, TEST_KEY)


class ClinicalDataContractTests(unittest.TestCase):
    def test_supported_loinc_codes_pass_without_mutating_input(self):
        observations = [
            {"obs_id": "synthetic-o1", "code": "8867-4"},
            {"obs_id": "synthetic-o2", "code": "2339-0"},
        ]
        original = copy.deepcopy(observations)

        result = ClinicalDataContractValidator.validate_observations(observations)

        self.assertEqual(observations, original)
        self.assertEqual(result["total_observations"], 2)
        self.assertEqual(result["invalid_codes"], 0)
        self.assertEqual(result["invalid_observations"], [])
        self.assertIs(result["passed"], True)

    def test_invalid_and_malformed_observations_return_diagnostics(self):
        observations = [
            {"obs_id": "synthetic-o1", "code": "unknown"},
            {"obs_id": "synthetic-o2"},
            None,
            "not-a-record",
        ]

        result = ClinicalDataContractValidator.validate_observations(observations)

        self.assertEqual(result["total_observations"], 4)
        self.assertEqual(result["invalid_codes"], 4)
        self.assertIs(result["passed"], False)
        self.assertEqual(
            [item["index"] for item in result["invalid_observations"]],
            [0, 1, 2, 3],
        )
        self.assertEqual(
            result["invalid_observations"][2]["reason"],
            "observation must be a dictionary",
        )

    def test_observations_must_be_a_list(self):
        for observations in (None, {}, ()):
            with self.subTest(observations=observations), self.assertRaises(TypeError):
                ClinicalDataContractValidator.validate_observations(observations)


if __name__ == "__main__":
    unittest.main()
