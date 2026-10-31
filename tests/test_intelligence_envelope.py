import copy
import json
from pathlib import Path
import unittest

from archaios_core.evidence import validate_record, validate_batch
from archaios_core.intelligence_envelope import validate_intelligence_record


class IntelligenceEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((Path(__file__).resolve().parents[1] /
            "research/fixtures/intelligence-draft.json").read_text())[0]

    def variant(self, **changes):
        result = copy.deepcopy(self.record)
        result.update(changes)
        return result

    def test_unplaced_unknowns_pass_without_mutation_or_promotion(self):
        before = copy.deepcopy(self.record)
        self.assertEqual(validate_record(self.record), [])
        self.assertEqual(self.record, before)
        self.assertEqual(self.record["category"], "CREATIVE_CONCEPT")
        self.assertEqual(self.record["reviewStatus"], "UNREVIEWED")

    def test_mode_kind_and_schema_required_even_with_remaining_intelligence_fields(self):
        for key in ("mode", "recordKind", "schemaVersion"):
            record = self.variant()
            del record[key]
            self.assertTrue(validate_record(record), key)
        for mode in (None, "", [], "LIVEish"):
            self.assertTrue(validate_record(self.variant(mode=mode)))

    def test_all_declared_mode_partitions_and_separate_prefixes(self):
        for mode, domain, store in (("LIVE", "intelligence", "intelligence/live"),
                ("CACHED", "intelligence", "intelligence/cached"),
                ("DEMO", "demo", "demo/events"),
                ("SIMULATION", "simulation", "simulation/events")):
            record = self.variant(mode=mode, domain=domain, store=store,
                recordId=f"{domain}:fixture:one")
            self.assertEqual(validate_record(record), [], mode)
            self.assertTrue(validate_record({**record, "store": "intelligence/live"})
                if mode != "LIVE" else validate_record({**record, "domain": "demo"}))
            self.assertTrue(validate_record({**record, "recordId": "qx:wrong-domain"}))

    def test_true_zero_and_coordinate_boundaries_preserved(self):
        for lat, lon in ((0, 0), (-90, -180), (90, 180), (12.5, -50.25)):
            record = self.variant(placement="PLACED", latitude=lat, longitude=lon)
            self.assertEqual(validate_record(record), [])
            self.assertEqual(record["latitude"], lat)
            self.assertEqual(record["longitude"], lon)

    def test_invalid_coordinates_rejected_without_coercion(self):
        for bad in (None, True, "0", float("nan"), float("inf"), [], 10 ** 500):
            self.assertTrue(validate_record(self.variant(placement="PLACED", latitude=bad, longitude=0)))
        self.assertTrue(validate_record(self.variant(placement="PLACED", latitude=90.001, longitude=0)))
        self.assertTrue(validate_record(self.variant(placement="PLACED", latitude=0, longitude=-180.01)))

    def test_unplaced_requires_both_explicit_nulls(self):
        self.assertTrue(validate_record(self.variant(latitude=0)))
        record = self.variant()
        del record["longitude"]
        self.assertTrue(validate_record(record))
        self.assertTrue(validate_record(self.variant(placement=None)))

    def test_incident_count_only_integer_or_null(self):
        for count in (None, 0, 3):
            self.assertEqual(validate_record(self.variant(incidentCount=count)), [])
        for count in (True, -1, 1.1, "3", float("nan"), {}):
            self.assertTrue(validate_record(self.variant(incidentCount=count)), str(count))

    def test_unknown_and_normalized_nested_forbidden_quantity_fields_fail(self):
        self.assertTrue(validate_record(self.variant(unreviewedExtension={"anything": 1})))
        # Rejected test data only; no such structured quantity enters accepted fixtures.
        for key in ("fatalities", "casualtyTotal", "DEATH_COUNT", "in-juries", "wounded"):
            record = self.variant()
            record["evidenceSources"][0][key] = 1
            errors = validate_record(record)
            self.assertTrue(any("forbidden structured quantity" in e for e in errors), key)
        self.assertTrue(validate_record(self.variant(incident_count=2)))

    def test_freshness_requires_separate_offset_instants_and_positive_cadence(self):
        self.assertTrue(validate_record(self.variant(freshnessStatus="current")))
        good = self.variant(sourceUpdatedAt="2026-10-31T05:00:00Z",
            retrievedAt="2026-10-31T05:01:00+00:00", sourceCadence=60,
            freshnessStatus="current", connectivity="connected")
        self.assertEqual(validate_record(good), [])
        for key in ("sourceUpdatedAt", "retrievedAt", "observedAt", "assessedAt"):
            self.assertTrue(validate_record({**good, key: "2026-10-31T05:00:00"}), key)
        for cadence in (0, -1, True, 60.5, "60"):
            self.assertTrue(validate_record({**good, "sourceCadence": cadence}))
        self.assertTrue(validate_record({**good, "sourceUpdatedAt": "2026-10-31T06:00:00Z"}))

    def test_source_ids_citations_and_assessment_coverage(self):
        for bad_url in ("file:///private/file", "https://user:secret@example.org", "https://[broken"):
            record = self.variant()
            record["evidenceSources"][0]["citation"] = bad_url
            self.assertTrue(validate_record(record))
        record = self.variant()
        record["evidenceSources"].append(copy.deepcopy(record["evidenceSources"][0]))
        self.assertTrue(validate_record(record))
        record = self.variant()
        record["sourceAssessment"]["sourceIds"] = ["different-source"]
        self.assertTrue(validate_record(record))
        self.assertTrue(validate_record(self.variant(coreClaims=[])))
        self.assertTrue(validate_record(self.variant(independenceRationale="")))

    def test_review_requires_declared_identity_scope_time_and_source_assessment(self):
        record = self.variant(reviewStatus="INDEPENDENTLY_REVIEWED")
        self.assertTrue(validate_record(record))
        record.update(reviewerIdentity={"id": "reviewer:fixture", "issuer": "synthetic-test-issuer"},
            assessedBy="reviewer:fixture", assessedAt="2026-10-31T05:10:00Z")
        record["sourceAssessment"]["status"] = "ASSESSED"
        before = copy.deepcopy(record)
        self.assertEqual(validate_record(record), [])
        self.assertEqual(record, before)  # accepted structure is not identity authentication
        self.assertTrue(validate_record({**record, "assessedBy": "reviewer:other"}))
        self.assertTrue(validate_record({**record, "reviewStatus": "UNREVIEWED"}))

    def test_declared_verification_requires_review_and_distinct_origins_but_never_promotes(self):
        record = self.variant(mode="LIVE", domain="intelligence", store="intelligence/live",
            recordId="intelligence:fixture:two-sources", category="VERIFIED", confidence="VERIFIED",
            reviewStatus="INDEPENDENTLY_REVIEWED",
            reviewerIdentity={"id": "reviewer:fixture", "issuer": "synthetic-issuer"},
            assessedBy="reviewer:fixture", assessedAt="2026-10-31T05:10:00Z")
        record["sourceAssessment"]["status"] = "ASSESSED"
        self.assertTrue(validate_record(record))
        record["evidenceSources"].append({"sourceId": "source-2", "citation": "https://example.org/two",
            "originId": "synthetic-origin-2"})
        record["sourceAssessment"]["sourceIds"].append("source-2")
        before = copy.deepcopy(record)
        self.assertEqual(validate_record(record), [])
        self.assertEqual(record, before)
        record["evidenceSources"][1]["originId"] = "synthetic-author"
        self.assertTrue(validate_record(record))

    def test_demo_and_simulation_cannot_claim_verified_or_measurement_lanes(self):
        self.assertTrue(validate_record(self.variant(category="VERIFIED")))
        self.assertTrue(validate_record(self.variant(confidence="VERIFIED")))
        self.assertTrue(validate_record(self.variant(claimType="MEASUREMENT")))
        self.assertTrue(validate_record(self.variant(mode="SIMULATION", domain="simulation",
            store="simulation/events", recordId="simulation:fixture:one", confidence="VERIFIED")))

    def test_batch_duplicate_ids_and_malformed_inputs(self):
        self.assertTrue(validate_batch([self.record, self.record])[1]["errors"])
        for bad in (None, [], "record"):
            self.assertTrue(validate_intelligence_record(bad))
        for key in ("sourceAssessment", "reviewerIdentity", "evidenceSources", "connectivity", "freshnessStatus"):
            self.assertTrue(validate_record(self.variant(**{key: []})), key)


if __name__ == "__main__":
    unittest.main()
