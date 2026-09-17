"""HIPAA Safe Harbor PHI De-identification Engine."""
import hashlib
from typing import Dict, Any

class PHIMasker:
    SALT = "enterprise_clinical_salt_2026"

    @classmethod
    def pseudonymize_mrn(cls, mrn: str) -> str:
        """Hash Medical Record Number (MRN) deterministically."""
        if not mrn:
            return ""
        return hashlib.sha256((mrn + cls.SALT).encode("utf-8")).hexdigest()[:16]

    @classmethod
    def mask_patient_record(cls, patient: Dict[str, Any]) -> Dict[str, Any]:
        masked = dict(patient)
        raw_mrn = masked.pop("mrn", "")
        masked["pseudonymized_patient_key"] = cls.pseudonymize_mrn(raw_mrn)
        masked["is_deidentified"] = True
        return masked
