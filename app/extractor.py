from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import MODEL_NAME
from app.schemas import ExtractionResult, Commitment
from typing import List

# No api_key parameter — reads from environment variable automatically
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0
)

parser = JsonOutputParser(pydantic_object=ExtractionResult)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert at extracting commitments from meeting transcripts.

Return ONLY valid JSON matching this format:
{{
  "commitments": [
    {{
      "task": "string",
      "owner": "string or null",
      "deadline": "string or null",
      "priority": "high|medium|low",
      "is_vague": true or false
    }}
  ]
}}"""
    ),
    (
        "human",
        "Extract all commitments from this meeting transcript:\n\n{transcript}"
    )
])

extraction_chain = prompt | llm | parser


def extract_commitments(transcript: str) -> List[Commitment]:
    result = extraction_chain.invoke({"transcript": transcript})
    commitments = [Commitment(**c) for c in result["commitments"]]
    return commitments