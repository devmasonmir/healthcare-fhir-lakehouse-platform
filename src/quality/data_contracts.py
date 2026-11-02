"""Clinical observation data contract validation."""

from typing import Any, Dict, List


class ClinicalDataContractValidator:
    """Validate the supported LOINC codes on parsed observations."""

    VALID_LOINC_CODES = {"8867-4", "8480-6", "8462-4", "2339-0"}

    @classmethod
    def validate_observations(
        cls,
        observations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Return a stable summary and diagnostics for invalid observations."""
        if not isinstance(observations, list):
            raise TypeError("observations must be a list")

        invalid = []
        for index, observation in enumerate(observations):
            if not isinstance(observation, dict):
                invalid.append({
                    "index": index,
                    "obs_id": None,
                    "code": None,
                    "reason": "observation must be a dictionary",
                })
                continue

            code = observation.get("code")
            if not isinstance(code, str) or code not in cls.VALID_LOINC_CODES:
                invalid.append({
                    "index": index,
                    "obs_id": observation.get("obs_id"),
                    "code": code,
                    "reason": "missing or unsupported LOINC code",
                })

        return {
            "total_observations": len(observations),
            "invalid_codes": len(invalid),
            "invalid_observations": invalid,
            "passed": not invalid,
        }
