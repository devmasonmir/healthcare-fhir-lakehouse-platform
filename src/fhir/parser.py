"""FHIR R4 Bundle parser with defensive handling of optional fields."""

from typing import Any, Dict, List


class FHIRParser:
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
    def parse_bundle(bundle: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        entries = bundle.get("entry", []) if isinstance(bundle, dict) else []
        if not isinstance(entries, list):
            entries = []

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
                coding = FHIRParser._first_mapping(
                    resource.get("code", {}).get("coding")
                    if isinstance(resource.get("code"), dict)
                    else None
                )
                quantity = resource.get("valueQuantity")
                if not isinstance(quantity, dict):
                    quantity = {}
                observations.append({
                    "obs_id": resource.get("id"),
                    "patient_id": FHIRParser._reference_id(resource.get("subject")),
                    "code": coding.get("code"),
                    "value": quantity.get("value"),
                    "unit": quantity.get("unit"),
                })

        return {"patients": patients, "observations": observations}
