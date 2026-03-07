import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# Your company (issuer) info for PDF header/footer
COMPANY_NAME = _get("COMPANY_NAME", "OMBJI")
COMPANY_ADDRESS = _get("COMPANY_ADDRESS", "")
COMPANY_ICE = _get("COMPANY_ICE", "")
COMPANY_IF = _get("COMPANY_IF", "")
COMPANY_RC = _get("COMPANY_RC", "")
COMPANY_CNSS = _get("COMPANY_CNSS", "")
COMPANY_DESIGNATION = _get("COMPANY_DESIGNATION", "TRANSPORT DE BETON")

# Default client (used when invoice has no client name/ICE)
COMPANY_CLIENT_NAME = _get("COMPANY_CLIENT_NAME", "")
COMPANY_CLIENT_ICE = _get("COMPANY_CLIENT_ICE", "")
