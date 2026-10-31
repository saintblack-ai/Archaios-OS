"""DRAFT integration protocols only. No durable implementation or consumer.

Implementers must prove these guarantees at a reviewed storage/auth boundary.
Merely implementing this Protocol's method names proves none of them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


@dataclass(frozen=True)
class EvidencePartition:
    domain: str
    store: str
    mode: str


@dataclass(frozen=True)
class ReviewAuditEntry:
    record_id: str
    record_version: int
    actor_id: str
    identity_issuer: str
    occurred_at: str
    action: str
    rationale: str
    previous_labels: Mapping[str, str]
    proposed_labels: Mapping[str, str]
    source_assessment_reference: str


class DraftEvidenceRepository(Protocol):
    """Future adapter boundary, intentionally not instantiated or implemented.

    Every operation must authenticate actor/issuer against approved identity,
    authorize the partition and operation, and reject cross-domain/store moves.
    IDs remain globally unique and reserved across stores, batches, concurrent
    writers, imports and deletion/tombstones. Stores/counters/search must remain
    partitioned. Review history is append-only and versioned, never overwritten.
    """

    def insert_new(self, record: Mapping[str, object], *, partition: EvidencePartition,
                   audit: ReviewAuditEntry) -> None:
        """Atomically reserve globally unique ID, insert draft and append audit.

        Reject an existing ID, invalid partition, or failed actor authorization.
        No category/confidence/reviewStatus promotion based on structural pass.
        """
        ...

    def append_review(self, *, record_id: str, expected_version: int,
                      partition: EvidencePartition, audit: ReviewAuditEntry) -> None:
        """Authorize human review and append with optimistic version checking.

        No automatic application of proposed labels; policy and explicit review
        decisions must be separately implemented and reviewed before integration.
        """
        ...
