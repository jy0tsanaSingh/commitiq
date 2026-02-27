from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import OPENAI_API_KEY, MODEL_NAME
from app.schemas import ExtractionResult, Commitment
from typing import List


# Initialize the LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=MODEL_NAME,
    temperature=0
)

# Output parser
parser = JsonOutputParser(pydantic_object=ExtractionResult)

# The prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert at extracting commitments from meeting transcripts.

Extract every commitment, action item, or promise made in the transcript.

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

# LangChain LCEL chain
extraction_chain = prompt | llm | parser


def extract_commitments(transcript: str) -> List[Commitment]:
    result = extraction_chain.invoke({"transcript": transcript})
    commitments = [Commitment(**c) for c in result["commitments"]]
    return commitments