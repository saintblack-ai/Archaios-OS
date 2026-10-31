"""Pure, strict DRAFT intelligence envelope checks; no persistence or promotion.

Review labels and identities are caller declarations. Validation cannot establish
their authenticity, credibility, independence, or correctness.
"""
from __future__ import annotations

from datetime import datetime
import re
from urllib.parse import urlsplit

SCHEMA_VERSION = "archaios.intelligence.draft.v1"
PARTITIONS = {
    "LIVE": ("intelligence", "intelligence/live"),
    "CACHED": ("intelligence", "intelligence/cached"),
    "DEMO": ("demo", "demo/events"),
    "SIMULATION": ("simulation", "simulation/events"),
}
COMMON_FIELDS = {
    "recordId", "claim", "source", "counterevidence", "provenance",
    "category", "confidence", "eventDate", "publishedDate", "retrievedAt",
    "reviewDate",
}
INTELLIGENCE_FIELDS = {
    "recordKind", "schemaVersion", "domain", "store", "mode", "placement",
    "latitude", "longitude", "incidentCount", "observedAt", "sourceUpdatedAt",
    "sourceCadence", "connectivity", "freshnessStatus", "evidenceSources",
    "coreClaims", "independenceRationale", "assessedAt", "assessedBy",
    "reviewerIdentity", "sourceAssessment", "reviewStatus",
}
ALLOWED_FIELDS = COMMON_FIELDS | INTELLIGENCE_FIELDS
CATEGORIES = {"VERIFIED", "UNVERIFIED_REPORT", "HYPOTHESIS",
              "THEOLOGICAL_INTERPRETATION", "CREATIVE_CONCEPT"}
CONFIDENCE = {"VERIFIED", "REPORTED", "ESTIMATED", "UNASSESSED"}
# Defense in depth in addition to the strict field allow-list. Normalize keys so
# case/punctuation variants cannot hide banned structured quantities.
FORBIDDEN_KEY_PARTS = ("fatalit", "casualt", "death", "injur", "killed", "wounded", "deadcount")


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _instant(value: object) -> datetime | None:
    if not isinstance(value, str) or "T" not in value:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result if result.utcoffset() is not None else None
    except ValueError:
        return None


def _forbidden_fields(value: object, path: str = "record", depth: int = 0) -> list[str]:
    if depth > 20:
        return [f"{path}: nesting exceeds draft limit"]
    errors = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z]", "", str(key).lower())
            if any(term in normalized for term in FORBIDDEN_KEY_PARTS):
                errors.append(f"{path}: forbidden structured quantity field")
            errors.extend(_forbidden_fields(child, f"{path}.{key}", depth + 1))
    elif isinstance(value, list):
        for child in value:
            errors.extend(_forbidden_fields(child, f"{path}[]", depth + 1))
    return errors


def validate_intelligence_record(record: object) -> list[str]:
    """Return structural errors; never rewrite, classify, or promote a claim."""
    if not isinstance(record, dict):
        return ["intelligence record must be an object"]
    errors = _forbidden_fields(record)
    unknown = set(record) - ALLOWED_FIELDS
    if unknown:
        errors.append("unknown intelligence fields are forbidden")
    for field in sorted(ALLOWED_FIELDS - set(record)):
        errors.append(f"{field}: required (explicit null where permitted)")
    if record.get("recordKind") != "INTELLIGENCE":
        errors.append("recordKind: INTELLIGENCE required")
    if record.get("schemaVersion") != SCHEMA_VERSION:
        errors.append("schemaVersion: unsupported draft version")
    for field in ("recordId", "claim", "source", "counterevidence", "provenance"):
        if not _text(record.get(field)):
            errors.append(f"{field}: nonempty text required")
    for field, allowed in (("category", CATEGORIES), ("confidence", CONFIDENCE)):
        if not isinstance(record.get(field), str) or record[field] not in allowed:
            errors.append(f"{field}: unsupported value")

    mode = record.get("mode")
    partition = PARTITIONS.get(mode) if isinstance(mode, str) else None
    if partition is None:
        errors.append("mode: LIVE, CACHED, DEMO or SIMULATION required")
    else:
        domain, store = partition
        if record.get("domain") != domain or record.get("store") != store:
            errors.append("domain/store: must match mode partition")
        record_id = record.get("recordId")
        if not isinstance(record_id, str) or not re.fullmatch(
                rf"{domain}:[A-Za-z0-9][A-Za-z0-9:_.-]{{0,190}}", record_id):
            errors.append("recordId: stable ID with matching domain prefix required")
    if mode in ("DEMO", "SIMULATION"):
        if record.get("confidence") != "UNASSESSED" or record.get("category") == "VERIFIED":
            errors.append("DEMO/SIMULATION cannot declare verified evidence")

    placement = record.get("placement")
    lat, lon = record.get("latitude"), record.get("longitude")
    if placement == "UNPLACED":
        if lat is not None or lon is not None:
            errors.append("UNPLACED requires null latitude and longitude")
    elif placement == "PLACED":
        for field, value, bound in (("latitude", lat, 90), ("longitude", lon, 180)):
            if (isinstance(value, bool) or not isinstance(value, (int, float)) or
                    not -bound <= value <= bound):
                errors.append(f"{field}: finite numeric value in [-{bound},{bound}] required")
    else:
        errors.append("placement: PLACED or UNPLACED required")
    count = record.get("incidentCount")
    if count is not None and (type(count) is not int or count < 0):
        errors.append("incidentCount: nonnegative integer or null required")

    instants = {}
    for field in ("observedAt", "sourceUpdatedAt", "retrievedAt", "assessedAt"):
        value = record.get(field)
        instant = _instant(value)
        instants[field] = instant
        if value is not None and instant is None:
            errors.append(f"{field}: timestamp with UTC offset or null required")
    for field in ("eventDate", "publishedDate", "reviewDate"):
        value = record.get(field)
        if value is not None:
            try:
                if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    raise ValueError
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                errors.append(f"{field}: calendar date YYYY-MM-DD or null required")
    cadence = record.get("sourceCadence")
    if cadence is not None and (type(cadence) is not int or cadence <= 0):
        errors.append("sourceCadence: positive integer seconds or null required")
    if record.get("connectivity") not in ("connected", "disconnected", "error", "unknown"):
        errors.append("connectivity: unsupported value")
    freshness = record.get("freshnessStatus")
    if freshness not in ("current", "delayed", "stale", "unknown", "error"):
        errors.append("freshnessStatus: unsupported value")
    if freshness in ("current", "delayed", "stale") and (
            not instants["sourceUpdatedAt"] or not instants["retrievedAt"] or
            type(cadence) is not int or cadence <= 0):
        errors.append("freshnessStatus: assessed freshness needs update/retrieval/cadence")
    for field in ("observedAt", "sourceUpdatedAt"):
        if instants[field] and instants["retrievedAt"] and instants[field] > instants["retrievedAt"]:
            errors.append(f"{field}: cannot be later than retrievedAt")

    sources = record.get("evidenceSources")
    source_ids, origin_ids = [], []
    if not isinstance(sources, list) or not sources:
        errors.append("evidenceSources: nonempty source list required")
    else:
        for source in sources:
            if not isinstance(source, dict) or set(source) != {"sourceId", "citation", "originId"}:
                errors.append("evidenceSources: exact sourceId/citation/originId fields required")
                continue
            if any(not _text(source[key]) for key in source):
                errors.append("evidenceSources: nonempty source metadata required")
                continue
            try:
                citation = urlsplit(source["citation"])
                valid_citation = (citation.scheme in ("https", "http") and citation.hostname and
                    not citation.username and not citation.password)
            except ValueError:
                valid_citation = False
            if not valid_citation:
                errors.append("evidenceSources: HTTP(S) citation without credentials required")
            source_ids.append(source["sourceId"])
            origin_ids.append(source["originId"])
        if len(source_ids) != len(set(source_ids)):
            errors.append("evidenceSources: duplicate sourceId")
    claims = record.get("coreClaims")
    if not isinstance(claims, list) or not claims or any(not _text(c) for c in claims):
        errors.append("coreClaims: nonempty list of nonempty text required")
    if not _text(record.get("independenceRationale")):
        errors.append("independenceRationale: explicit assessment or unknown explanation required")

    source_assessment = record.get("sourceAssessment")
    if (not isinstance(source_assessment, dict) or
            set(source_assessment) != {"status", "rationale", "sourceIds"}):
        errors.append("sourceAssessment: exact status/rationale/sourceIds required")
    else:
        assessed_ids = source_assessment["sourceIds"]
        if (source_assessment["status"] not in ("UNASSESSED", "ASSESSED") or
                not _text(source_assessment["rationale"]) or
                not isinstance(assessed_ids, list) or
                any(not _text(i) for i in assessed_ids) or
                len(assessed_ids) != len(set(assessed_ids)) or
                set(assessed_ids) != set(source_ids)):
            errors.append("sourceAssessment: status/rationale and exact unique source coverage required")
    review = record.get("reviewStatus")
    identity = record.get("reviewerIdentity")
    if review == "UNREVIEWED":
        if any(record.get(k) is not None for k in ("reviewerIdentity", "assessedBy", "assessedAt")):
            errors.append("UNREVIEWED requires null reviewer identity/by/time")
        if isinstance(source_assessment, dict) and source_assessment.get("status") != "UNASSESSED":
            errors.append("UNREVIEWED sourceAssessment must be UNASSESSED")
    elif review == "INDEPENDENTLY_REVIEWED":
        if (not isinstance(identity, dict) or set(identity) != {"id", "issuer"} or
                any(not _text(identity[k]) for k in identity)):
            errors.append("reviewerIdentity: exact nonempty id/issuer required")
        elif record.get("assessedBy") != identity["id"]:
            errors.append("assessedBy must match declared reviewerIdentity.id")
        if not instants["assessedAt"]:
            errors.append("reviewed record needs assessedAt timestamp")
        if isinstance(source_assessment, dict) and source_assessment.get("status") != "ASSESSED":
            errors.append("reviewed sourceAssessment must be ASSESSED")
    else:
        errors.append("reviewStatus: unsupported value")
    if record.get("category") == "VERIFIED" or record.get("confidence") == "VERIFIED":
        if review != "INDEPENDENTLY_REVIEWED" or len(set(origin_ids)) < 2:
            errors.append("declared VERIFIED needs review and two declared independent origins")
    return errors
