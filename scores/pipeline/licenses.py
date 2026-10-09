"""License gate. Rules L1-L5 in scores/RULES.md.

A file is processed only if every rule passes. Otherwise we refuse and say why.
"""
import csv
import re
from pathlib import Path

ALLOWED_DERIVATIVES = {"yes", "share-alike"}
ALLOWED_FORMATS = {"musicxml", "mxl", "xml"}


def load_assets(csv_path):
    """Read licenses/assets.csv into {asset_id: row}."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        return {row["asset_id"].strip(): row for row in csv.DictReader(f) if row.get("asset_id")}


def is_no_derivatives(license_text):
    """True if a license string names a No-Derivatives license (ND)."""
    text = (license_text or "").upper().replace("_", "-").replace(" ", "-")
    return bool(re.search(r"(^|-)ND($|-)", text)) or "NODERIV" in text.replace("-", "")


def check_license(asset_id, row):
    """Return (ok, reasons). reasons lists every rule that failed."""
    if row is None:
        return False, [f"L1: no row for '{asset_id}' in licenses/assets.csv. Add one first."]
    reasons = []
    status = (row.get("composition_status") or "").strip().lower()
    if status in ("", "unknown"):
        reasons.append("L2: composition_status is empty or 'unknown'.")
    deriv = (row.get("derivatives_allowed") or "").strip().lower()
    if deriv not in ALLOWED_DERIVATIVES:
        reasons.append(f"L3: derivatives_allowed is '{deriv or 'empty'}'. It must be 'yes' or 'share-alike'.")
    lic = row.get("edition_license", "")
    if is_no_derivatives(lic):
        reasons.append(f"L4: edition_license '{lic}' is No-Derivatives (ND). We may not simplify it.")
    if not (row.get("verified_by") or "").strip():
        reasons.append("L5: verified_by is empty. A person must check the license first.")
    fmt = (row.get("source_format") or "").strip().lower()
    if fmt not in ALLOWED_FORMATS:
        reasons.append(f"L6: source_format is '{fmt or 'empty'}'. It must be musicxml, mxl, or xml.")
    return (not reasons), reasons


def find_source_file(source_dir, asset_id):
    """The source file must be named <asset_id>.musicxml, .mxl, or .xml."""
    for ext in (".musicxml", ".mxl", ".xml"):
        p = Path(source_dir) / f"{asset_id}{ext}"
        if p.exists():
            return p
    return None
