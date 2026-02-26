from app.schemas import Commitment, RiskFlag
from app.memory import get_commitments_by_owner, search_similar_commitments
from typing import List


# ─── Individual Risk Checks ───────────────────────────────────

def check_no_owner(commitment: Commitment) -> RiskFlag | None:
    if not commitment.owner:
        return RiskFlag(
            type="no_owner",
            task=commitment.task,
            severity="high",
            insight=f"No owner assigned for: '{commitment.task}'"
        )
    return None


def check_no_deadline(commitment: Commitment) -> RiskFlag | None:
    if not commitment.deadline:
        return RiskFlag(
            type="no_deadline",
            task=commitment.task,
            owner=commitment.owner,
            severity="medium",
            insight=f"No deadline set for: '{commitment.task}'"
        )
    return None


def check_vague_commitment(commitment: Commitment) -> RiskFlag | None:
    if commitment.is_vague:
        return RiskFlag(
            type="vague_commitment",
            task=commitment.task,
            owner=commitment.owner,
            severity="medium",
            insight=f"Vague commitment with no clear action: '{commitment.task}'"
        )
    return None


def check_overloaded_owner(commitment: Commitment) -> RiskFlag | None:
    if not commitment.owner:
        return None
    existing = get_commitments_by_owner(commitment.owner)
    open_count = len([c for c in existing if c["status"] == "open"])
    if open_count > 4:
        return RiskFlag(
            type="overloaded_owner",
            task=commitment.task,
            owner=commitment.owner,
            severity="high",
            insight=f"{commitment.owner} has {open_count} open commitments — overloaded"
        )
    return None


def check_repeated_topic(commitment: Commitment, current_meeting_id: str = None) -> RiskFlag | None:
    """
    Searches ChromaDB for similar past commitments.
    Only flags if found in a DIFFERENT meeting.
    This is the cross-meeting intelligence feature.
    """
    results = search_similar_commitments(commitment.task, n_results=5)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    # Only count results from different meetings
    different_meeting_matches = [
        doc for doc, meta in zip(documents, metadatas)
        if meta.get("meeting_id") != current_meeting_id
        and doc.lower() != commitment.task.lower()
    ]

    if len(different_meeting_matches) >= 1:
        return RiskFlag(
            type="repeated_topic",
            task=commitment.task,
            owner=commitment.owner,
            severity="high",
            insight=f"'{commitment.task}' has appeared in previous meetings without resolution"
        )
    return None


# ─── Run All Checks ───────────────────────────────────────────

def detect_risks(commitments: List[Commitment], meeting_id: str = None) -> List[RiskFlag]:
    """
    Runs all risk checks on every commitment.
    Returns list of all flags found.
    """
    flags = []

    for commitment in commitments:
        checks = [
            check_no_owner(commitment),
            check_no_deadline(commitment),
            check_vague_commitment(commitment),
            check_overloaded_owner(commitment),
            check_repeated_topic(commitment, current_meeting_id=meeting_id),
        ]
        flags.extend([f for f in checks if f is not None])

    return flags


# ─── Health Score ─────────────────────────────────────────────

def calculate_health_score(flags: List[RiskFlag]) -> tuple[int, str]:
    """
    Calculates execution health score from 0 to 100.
    Returns score and label.
    """
    score = 100

    for flag in flags:
        if flag.type == "no_owner":
            score -= 15
        elif flag.type == "repeated_topic":
            score -= 12
        elif flag.type == "no_deadline":
            score -= 10
        elif flag.type == "overloaded_owner":
            score -= 10
        elif flag.type == "vague_commitment":
            score -= 8

    score = max(score, 0)

    if score >= 75:
        label = "Healthy"
    elif score >= 50:
        label = "At Risk"
    else:
        label = "Critical"

    return score, label