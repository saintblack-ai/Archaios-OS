# ARCHAIOS / QX evidence intake — local draft

This standalone, standard-library Python module implements a first subset of
Muse's Polymath Bridge v1.0 sections 3.1 and 3.3. It has no network calls and does
not change orchestration, scheduled jobs, existing agent output, or databases.

Run from the repository root:

```bash
python -m archaios_core.evidence research/fixtures/qx-concept.json
python -m unittest discover -s tests -v
```

The CLI reads a JSON array, prints structured validation output and exits 1 on
invalid records or input. It requires provenance, counterevidence, explicit date
fields (null for unknowns), category, confidence, and stable IDs. Duplicate IDs
are refused within a batch. QX records require a `qx:` namespace, result lane,
review status and instrument/model, reference, quantity and uncertainty fields.
Result records need populated metadata. Concept metadata may be explicitly null.
DEMO confidence stays UNASSESSED. SIMULATION_RESULT requires SIMULATION mode;
SIMULATION and DEMO records cannot be MEASUREMENT records.

This is structural validation. It cannot determine whether a source is credible,
whether a claimed measurement occurred, whether sources are independent, or
whether a result is scientifically sound. A supplied VERIFIED label is not
independent verification. Never automatically promote a record on validation.

The fixture is a synthetic software-contract concept, not a research finding.
No QX hardware, physical experiment, or scientific simulation was performed.

## Remaining integration work

- Review the draft envelope before adopting it as the house standard.
- A separate strict intelligence draft now checks mode, coordinates/unplaced
  records, incident-only fields, freshness/cadence, provenance/source assessment
  and declared reviewer identity. See [v1.2 schema and limits](EVIDENCE_NEXT_INCREMENT_v1.2.md).
- Persistent ID uniqueness, authorization, domain/store separation and append-only
  audit history have Protocol-only boundaries, not durable implementations.
- QLE retains the owner-authored Quandrix Light Equation meaning; this module
  does not evaluate, redefine or treat it as a physical law.
- Integrate through a reviewed PR with the existing orchestrator only after
  acceptance criteria are agreed. Existing QX agents currently generate planning
  outlines; those outlines are not new experimental results.

Source design: https://docs.google.com/document/d/1ApU4NpiC-7m8e9oqWUQhwhDGtpw7Px4U9emYytEpK4M/edit

Validation: 21 unit tests (7 original QX and 14 intelligence draft tests) pass.
Both synthetic fixture CLIs pass. Structural acceptance is not source assessment
or authenticated review. Production and Living Theater remain unchanged.
