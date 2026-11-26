"""FHIR R4 Bundle parser with defensive handling of optional fields."""

from typing import Any, Dict, List


class FHIRParser:
    LOINC_SYSTEM = "http://loinc.org"

    @staticmethod
    def _first_mapping(value: Any) -> Dict[str, Any]:
        """Return the first object from a FHIR repeating element."""
        if not isinstance(value, list):
            return {}
        return next((item for item in value if isinstance(item, dict)), {})

    @staticmethod
    def _reference_id(subject: Any) -> Any:
        """Remove only a leading Patient/ prefix from a subject reference."""
        if not isinstance(subject, dict):
            return None

        reference = subject.get("reference")
        if not isinstance(reference, str) or not reference:
            return None
        if reference.startswith("Patient/"):
            return reference[len("Patient/"):] or None
        return reference

    @staticmethod
    def _observation_code(code: Any) -> Any:
        """Prefer an explicit LOINC coding while retaining first-code fallback."""
        if not isinstance(code, dict):
            return None

        codings = code.get("coding")
        if not isinstance(codings, list):
            return None

        first_coding = FHIRParser._first_mapping(codings)
        for coding in codings:
            if not isinstance(coding, dict):
                continue
            candidate = coding.get("code")
            if (
                coding.get("system") == FHIRParser.LOINC_SYSTEM
                and isinstance(candidate, str)
                and candidate
            ):
                return candidate
        return first_coding.get("code")

    @staticmethod
    def parse_bundle(bundle: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Parse a bundle object while isolating malformed entry records."""
        if not isinstance(bundle, dict):
            raise TypeError("bundle must be a dictionary")

        entries = bundle.get("entry", [])
        if not isinstance(entries, list):
            raise TypeError("bundle entry must be a list")

        patients = []
        observations = []

        for item in entries:
            if not isinstance(item, dict):
                continue
            resource = item.get("resource", {})
            if not isinstance(resource, dict):
                continue

            rtype = resource.get("resourceType")
            if rtype == "Patient":
                identifier = FHIRParser._first_mapping(resource.get("identifier"))
                patients.append({
                    "patient_id": resource.get("id"),
                    "gender": resource.get("gender"),
                    "birth_date": resource.get("birthDate"),
                    "mrn": identifier.get("value"),
                })
            elif rtype == "Observation":
                quantity = resource.get("valueQuantity")
                if not isinstance(quantity, dict):
                    quantity = {}
                observations.append({
                    "obs_id": resource.get("id"),
                    "patient_id": FHIRParser._reference_id(resource.get("subject")),
                    "code": FHIRParser._observation_code(resource.get("code")),
                    "value": quantity.get("value"),
                    "unit": quantity.get("unit"),
                })

        return {"patients": patients, "observations": observations}
