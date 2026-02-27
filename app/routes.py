from fastapi import APIRouter, HTTPException
from app.schemas import (
    IngestRequest, IngestResponse,
    QueryRequest, QueryResponse,
    Commitment, RiskFlag
)
from app.extractor import extract_commitments
from app.memory import (
    save_meeting, save_commitments,
    get_all_commitments, get_commitments_by_owner,
    search_similar_commitments, init_db
)
from app.risk_engine import detect_risks, calculate_health_score
from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY, MODEL_NAME
import uuid

router = APIRouter()

llm = ChatOpenAI(model=MODEL_NAME, temperature=0)

# ─── Ingest Meeting ───────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse)
def ingest_meeting(request: IngestRequest):
    """
    Main endpoint.
    Takes raw transcript → extracts commitments → 
    saves to memory → detects risks → returns health score.
    """
    try:
        #  Extract commitments using LangChain
        commitments = extract_commitments(request.content)

        if not commitments:
            raise HTTPException(status_code=400, detail="No commitments found in transcript")

        #  Save meeting to SQLite
        meeting_id = save_meeting(request.meeting_title)

        # Save commitments to SQLite + ChromaDB
        save_commitments(meeting_id, request.meeting_title, commitments)

        # Detect risks
        flags = detect_risks(commitments, meeting_id=meeting_id)

        # Calculate health score
        score, label = calculate_health_score(flags)

        return IngestResponse(
            meeting_id=meeting_id,
            meeting_title=request.meeting_title,
            commitments_extracted=len(commitments),
            health_score=score,
            health_label=label,
            commitments=commitments,
            risk_flags=flags
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Get All Commitments ──────────────────────────────────────

@router.get("/commitments")
def get_commitments(owner: str = None):
    """
    Returns all commitments.
    Optional filter by owner name.
    Example: /commitments?owner=Abhishek
    """
    if owner:
        results = get_commitments_by_owner(owner)
    else:
        results = get_all_commitments()

    return {"total": len(results), "commitments": results}


# ─── Get Health Score ─────────────────────────────────────────

@router.get("/health-score")
def get_health_score():
    """
    Calculates current health score across all commitments.
    """
    all_commitments = get_all_commitments()

    commitment_objects = [
        Commitment(
            task=c["task"],
            owner=c["owner"],
            deadline=c["deadline"],
            priority=c["priority"],
            is_vague=bool(c["is_vague"])
        )
        for c in all_commitments
    ]

    flags = detect_risks(commitment_objects)
    score, label = calculate_health_score(flags)

    return {
        "health_score": score,
        "health_label": label,
        "total_commitments": len(all_commitments),
        "total_risks": len(flags)
    }


# ─── Get Risk Flags ───────────────────────────────────────────

@router.get("/risks")
def get_risks():
    """
    Returns all current risk flags across all commitments.
    """
    all_commitments = get_all_commitments()

    commitment_objects = [
        Commitment(
            task=c["task"],
            owner=c["owner"],
            deadline=c["deadline"],
            priority=c["priority"],
            is_vague=bool(c["is_vague"])
        )
        for c in all_commitments
    ]

    flags = detect_risks(commitment_objects)

    return {
        "total_risks": len(flags),
        "risks": [f.dict() for f in flags]
    }


# ─── Natural Language Query ───────────────────────────────────

@router.post("/query", response_model=QueryResponse)
def query_commitments(request: QueryRequest):
    """
    Natural language question answered using ChromaDB memory.
    This is the cross-meeting intelligence feature.
    Example: "What has Abhishek committed to this month?"
    """
    try:
        # Search ChromaDB semantically
        results = search_similar_commitments(request.question, n_results=5)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return QueryResponse(
                question=request.question,
                answer="No relevant commitments found in memory."
            )

        # Build context for LLM
        context = "\n".join([
            f"- Task: {doc} | Owner: {meta.get('owner')} | "
            f"Deadline: {meta.get('deadline')} | "
            f"Meeting: {meta.get('meeting_title')} | "
            f"Status: {meta.get('status')}"
            for doc, meta in zip(documents, metadatas)
        ])

        # Ask LLM to answer using context
        prompt = f"""You are an execution intelligence assistant.
Based on these commitments from past meetings:

{context}

Answer this question clearly and concisely: {request.question}"""

        answer = llm.invoke(prompt)

        return QueryResponse(
            question=request.question,
            answer=answer.content
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))