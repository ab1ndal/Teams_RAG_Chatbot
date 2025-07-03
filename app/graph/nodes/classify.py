# app/graph/nodes/classify.py
from pydantic import BaseModel, Field
from typing import Literal
from langchain_openai import ChatOpenAI
from app.graph.state import AssistantState
from app.config import JSON_DESCRIPTION

class QueryClassification(BaseModel):
    query_class: Literal["excel_insight", "rfi_lookup", "general"] = Field(
        ..., 
        description="Classify if the message requires analytics on Excel files, wants information on the contents of specific RFIs, or is a general question"
    )

def classify_query(client: ChatOpenAI):
    structured_llm = client.with_structured_output(QueryClassification)

    def _node(state: AssistantState):
        last_message = state["messages"][-1] if state.get("messages") else {"content": ""}
        system_prompt = f"""
        You are a router for an assistant that classifies user queries into one of three categories:

        1. **excel_insight**: Queries that involve structured data analysis or retrieval from an Excel-based RFI log. This includes:
           - Summarizing, filtering, counting, grouping, or computing time-based insights
           - Answering questions about specific entries or attributes stored in the log
           - Queries that rely on structured fields such as dates, statuses, internal notes, file links, and numeric IDs
           - If the query can be answered by referencing structured tabular values described in the JSON schema below, it belongs in this class

        2. **rfi_lookup**: Queries that require accessing or quoting the full document content of a specific RFI, or locating its original folder or file.
           - This includes questions about what a document “says” or requests to "open", "find", or "read" a particular RFI file

        3. **general**: Any other query unrelated to structured RFI logs or document lookup. These may include questions about company history, projects, scheduling, people, or unrelated topics.

        Here is the JSON schema describing the fields available in the Excel RFI log:
        {JSON_DESCRIPTION}

        Use this to decide whether the query is answerable from structured Excel data or requires direct access to the document text.

        Respond only with a JSON object matching the schema.
        """
        response = structured_llm.invoke([
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": last_message["content"]}
        ])
        state["query_class"] = response.query_class
        return state
    return _node
    