"""Standalone draft intake contract. Validation checks structure, not truth.

Not connected to production routing, publishing, or existing agent outputs.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from archaios_core.intelligence_envelope import (
    INTELLIGENCE_FIELDS, validate_intelligence_record,
)

CATEGORIES = {"VERIFIED", "UNVERIFIED_REPORT", "HYPOTHESIS",
              "THEOLOGICAL_INTERPRETATION", "CREATIVE_CONCEPT"}
CONFIDENCE = {"VERIFIED", "REPORTED", "ESTIMATED", "UNASSESSED"}
CLAIM_TYPES = {"MEASUREMENT", "SIMULATION_RESULT", "FEASIBILITY_ASSESSMENT", "CONCEPT"}


def validate_record(record: object) -> list[str]:
    """Return all contract errors without mutating or promoting a record."""
    if not isinstance(record, dict):
        return ["record must be an object"]
    record_id = record.get("recordId")
    looks_intelligence = (record.get("recordKind") == "INTELLIGENCE" or
        (isinstance(record_id, str) and record_id.startswith(("intelligence:", "demo:", "simulation:"))) or
        bool((INTELLIGENCE_FIELDS - {"mode", "reviewStatus"}) & set(record)))
    if looks_intelligence:
        return validate_intelligence_record(record)
    errors: list[str] = []
    for field in ("recordId", "claim", "source", "counterevidence", "provenance"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"{field}: nonempty text required")
    for field, allowed in (("category", CATEGORIES), ("confidence", CONFIDENCE)):
        value = record.get(field)
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"{field}: unsupported value")
    for field in ("eventDate", "publishedDate", "retrievedAt", "reviewDate"):
        if field not in record:
            errors.append(f"{field}: required (null when unknown)")
        elif record[field] is not None:
            try:
                if not isinstance(record[field], str):
                    raise ValueError
                datetime.fromisoformat(record[field].replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{field}: ISO date or null required")
    mode = record.get("mode")
    if mode is not None and mode not in ("LIVE", "CACHED", "DEMO", "SIMULATION"):
        errors.append("mode: unsupported value")
    if mode == "DEMO" and record.get("confidence") != "UNASSESSED":
        errors.append("DEMO confidence must be UNASSESSED")

    # QX records are namespaced and carry an explicit result lane.
    is_qx = str(record.get("recordId", "")).startswith("qx:")
    if is_qx or "claimType" in record:
        if not is_qx:
            errors.append("QX recordId must start with qx:")
        claim_type = record.get("claimType")
        if not isinstance(claim_type, str) or claim_type not in CLAIM_TYPES:
            errors.append("claimType: unsupported QX lane")
        for field in ("instrumentOrModel", "referenceStandard", "measuredQuantity", "uncertainty"):
            if field not in record or (record[field] is not None and
                (not isinstance(record[field], str) or not record[field].strip())):
                errors.append(f"{field}: text or explicit null required")
        if record.get("reviewStatus") not in ("UNREVIEWED", "INDEPENDENTLY_REVIEWED"):
            errors.append("reviewStatus: unsupported value")
        if claim_type == "SIMULATION_RESULT" and mode != "SIMULATION":
            errors.append("simulation results require mode SIMULATION")
        if mode in ("SIMULATION", "DEMO") and claim_type == "MEASUREMENT":
            errors.append("simulated/demo data cannot be a measurement")
        if claim_type == "CONCEPT" and record.get("category") != "CREATIVE_CONCEPT":
            errors.append("QX concepts require category CREATIVE_CONCEPT")
        if claim_type in ("MEASUREMENT", "SIMULATION_RESULT"):
            for field in ("instrumentOrModel", "referenceStandard", "measuredQuantity", "uncertainty"):
                if not record.get(field):
                    errors.append(f"{field}: required for result records")
    return errors


def validate_batch(records: object) -> list[dict]:
    """Validate an intake batch, refusing duplicate IDs inside this batch."""
    if not isinstance(records, list):
        return [{"index": None, "errors": ["batch must be an array"]}]
    seen: set[str] = set()
    results = []
    for index, record in enumerate(records):
        errors = validate_record(record)
        record_id = record.get("recordId") if isinstance(record, dict) else None
        if isinstance(record_id, str):
            if record_id in seen:
                errors.append("duplicate recordId in batch")
            seen.add(record_id)
        results.append({"index": index, "errors": errors})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        records = json.loads(args.path.read_text())
        results = validate_batch(records)
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1
    valid = not any(result["errors"] for result in results)
    print(json.dumps({"valid": valid, "scope": "draft_structural_validation_only", "results": results}, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
