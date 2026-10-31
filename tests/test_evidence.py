import copy
import json
from pathlib import Path
import unittest

from archaios_core.evidence import validate_record, validate_batch


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((Path(__file__).resolve().parents[1] /
            "research/fixtures/qx-concept.json").read_text())[0]

    def test_concept_accepts_explicit_unknowns_without_mutation(self):
        before = copy.deepcopy(self.record)
        self.assertEqual(validate_record(self.record), [])
        self.assertEqual(self.record, before)

    def test_missing_provenance_counterevidence_and_dates_fail(self):
        for field in ("provenance", "counterevidence", "eventDate", "retrievedAt"):
            record = dict(self.record)
            del record[field]
            self.assertTrue(validate_record(record), field)

    def test_simulation_cannot_be_recorded_as_measurement(self):
        for mode in ("SIMULATION", "DEMO"):
            record = {**self.record, "mode": mode, "claimType": "MEASUREMENT"}
            self.assertIn("simulated/demo data cannot be a measurement", validate_record(record))

    def test_simulation_result_requires_label_and_result_metadata(self):
        record = {**self.record, "claimType": "SIMULATION_RESULT"}
        self.assertTrue(validate_record(record))
        record.update(mode="SIMULATION", instrumentOrModel="synthetic model",
            referenceStandard="fixture baseline", measuredQuantity="synthetic units",
            uncertainty="not a physical measurement; fixture only")
        self.assertEqual(validate_record(record), [])

    def test_demo_never_acquires_verified_confidence(self):
        record = {**self.record, "mode": "DEMO", "confidence": "VERIFIED"}
        self.assertIn("DEMO confidence must be UNASSESSED", validate_record(record))

    def test_duplicate_ids_fail(self):
        self.assertTrue(validate_batch([self.record, self.record])[1]["errors"])

    def test_invalid_types_and_dates_return_errors(self):
        for record in (None, [], "text", {**self.record, "category": []},
                       {**self.record, "eventDate": "2026-02-30"},
                       {**self.record, "mode": []},
                       {**self.record, "claimType": []}):
            self.assertTrue(validate_record(record))


if __name__ == "__main__":
    unittest.main()
