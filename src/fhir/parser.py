"""FHIR R4 Bundle Parser."""
from typing import Dict, Any, List

class FHIRParser:
    @staticmethod
    def parse_bundle(bundle: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        entries = bundle.get("entry", [])
        patients = []
        observations = []

        for item in entries:
            resource = item.get("resource", {})
            rtype = resource.get("resourceType")
            if rtype == "Patient":
                patients.append({
                    "patient_id": resource.get("id"),
                    "gender": resource.get("gender"),
                    "birth_date": resource.get("birthDate"),
                    "mrn": resource.get("identifier", [{}])[0].get("value")
                })
            elif rtype == "Observation":
                observations.append({
                    "obs_id": resource.get("id"),
                    "patient_id": resource.get("subject", {}).get("reference", "").replace("Patient/", ""),
                    "code": resource.get("code", {}).get("coding", [{}])[0].get("code"),
                    "value": resource.get("valueQuantity", {}).get("value"),
                    "unit": resource.get("valueQuantity", {}).get("unit")
                })

        return {"patients": patients, "observations": observations}
