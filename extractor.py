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

# Output parser tied to our Pydantic schema
parser = JsonOutputParser(pydantic_object=ExtractionResult)

# The prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert at extracting commitments from meeting transcripts.

Extract every commitment, action item, or promise made in the transcript.

For each commitment return:
- task: what needs to be done (clear, specific string)
- owner: person responsible (null if not mentioned)
- deadline: due date as string like "2024-02-15" or "next Friday" (null if not mentioned)
- priority: "high", "medium", or "low" based on context
- is_vague: true if the commitment is unclear or has no specific action

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

# The chain — this is LangChain LCEL syntax
extraction_chain = prompt | llm | parser


def extract_commitments(transcript: str) -> List[Commitment]:
    """
    Takes raw transcript text.
    Returns list of structured Commitment objects.
    """
    result = extraction_chain.invoke({"transcript": transcript})
    commitments = [Commitment(**c) for c in result["commitments"]]
    return commitments