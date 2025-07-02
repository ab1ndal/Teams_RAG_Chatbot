# app/graph/nodes/classify.py
from pydantic import BaseModel, Field
from typing import Literal
from langchain_openai import ChatOpenAI
from app.graph.state import AssistantState

class QueryClassification(BaseModel):
    query_class: Literal["excel_insight", "rfi_lookup", "general"] = Field(
        ..., 
        description="Classify if the message requires analytics on Excel files, wants information on the contents of specific RFIs, or is a general question"
    )

def classify_query(client: ChatOpenAI):
    structured_llm = client.with_structured_output(QueryClassification)

    def _node(state: AssistantState):
        last_message = state["messages"][-1] if state.get("messages") else {"content": ""}
        system_prompt = """
        You are a router for an assistant that classifies user queries into one of three categories:

        1. **excel_insight**: Queries that require analyzing structured Excel logs. These involve tasks such as summarizing, filtering, counting, computing durations, or finding trends across multiple RFIs stored in a spreadsheet. Examples:
        - "How many RFIs are still open?"
        - "Show the average turnaround time for RFIs last month"
        - "List all unanswered RFIs and how long they have been pending"

        2. **rfi_lookup**: Queries that ask for the full content, folder path, or server location of specific RFIs. These are lookup-style questions involving filenames or document access. Examples:
        - "Open RFI 0032 and tell me what it says"
        - "What did we respond in RFI 0045?"
        - "Find the folder for RFI 0023.1"

        3. **general**: Any other queries unrelated to the Excel data or RFI documents. These may involve general company questions, external topics, or casual queries. Examples:
        - "Who is our client on this project?"
        - "What does NYA specialize in?"

        Respond only with a JSON object matching the schema.
        """
        response = structured_llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": last_message["content"]}
        ])
        state["query_class"] = response.query_class
        return state
    return _node
    