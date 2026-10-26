"""Privacy helpers for deterministic clinical identifier pseudonymization."""

import hashlib
import hmac
import os
from typing import Any, Dict, Optional


class PHIMasker:
    """Pseudonymize MRNs with a secret that is kept outside source control."""

    KEY_ENV_VAR = "PHI_PSEUDONYMIZATION_KEY"
    MIN_KEY_BYTES = 32

    @classmethod
    def _resolve_key(cls, key: Optional[str]) -> bytes:
        candidate = key if key is not None else os.getenv(cls.KEY_ENV_VAR)
        if not isinstance(candidate, str) or not candidate:
            raise ValueError(
                f"Provide a key or set {cls.KEY_ENV_VAR}; no built-in key is used."
            )

        key_bytes = candidate.encode("utf-8")
        if len(key_bytes) < cls.MIN_KEY_BYTES:
            raise ValueError(
                f"{cls.KEY_ENV_VAR} must be at least {cls.MIN_KEY_BYTES} bytes."
            )
        return key_bytes

    @classmethod
    def pseudonymize_mrn(cls, mrn: str, key: Optional[str] = None) -> str:
        """Return a deterministic 128-bit HMAC token for a non-empty MRN."""
        if mrn is None or mrn == "":
            return ""
        if not isinstance(mrn, str):
            raise TypeError("mrn must be a string")

        digest = hmac.new(
            cls._resolve_key(key),
            mrn.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return digest[:32]

    @classmethod
    def mask_patient_record(
        cls,
        patient: Dict[str, Any],
        key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Copy a patient record, remove its MRN, and add an HMAC token."""
        if not isinstance(patient, dict):
            raise TypeError("patient must be a dictionary")

        masked = dict(patient)
        raw_mrn = masked.pop("mrn", "")
        masked["pseudonymized_patient_key"] = cls.pseudonymize_mrn(raw_mrn, key)
        masked["is_mrn_pseudonymized"] = True
        return masked
