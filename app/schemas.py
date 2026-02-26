from pydantic import BaseModel
from typing import Optional, List


# What comes INTO the API
class IngestRequest(BaseModel):
    meeting_title: str
    content: str


# A single commitment extracted by AI
class Commitment(BaseModel):
    task: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    is_vague: bool = False


# What the AI extraction chain returns
class ExtractionResult(BaseModel):
    commitments: List[Commitment]


# A single risk flag
class RiskFlag(BaseModel):
    type: str
    task: Optional[str] = None
    owner: Optional[str] = None
    severity: str
    insight: str


# Full API response after ingesting a meeting
class IngestResponse(BaseModel):
    meeting_id: str
    meeting_title: str
    commitments_extracted: int
    health_score: int
    health_label: str
    commitments: List[Commitment]
    risk_flags: List[RiskFlag]


# For the /query endpoint
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str