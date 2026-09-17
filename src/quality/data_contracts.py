"""Clinical Vocabulary & Code Validator."""
from typing import List, Dict, Any

class ClinicalDataContractValidator:
    # Standard LOINC codes for common lab observations
    VALID_LOINC_CODES = {"8867-4", "8480-6", "8462-4", "2339-0"}

    @classmethod
    def validate_observations(cls, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        invalid = []
        for obs in observations:
            code = obs.get("code")
            if code not in cls.VALID_LOINC_CODES:
                invalid.append({"obs_id": obs.get("obs_id"), "code": code})
        return {
            "total_observations": len(observations),
            "invalid_codes": len(invalid),
            "passed": len(invalid) == 0
        }
