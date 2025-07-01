# app/graph/nodes/classify.py
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI
from app.graph.state import AssistantState

class QueryClassification(BaseModel):
    query_class: Literal["excel_insight", "rfi_lookup", "general"] = Field(
        ..., 
        description="Classify if the message requires analytics on Excel files, wants information on the contents of specific RFIs, or is a general question"
    )

def classify_query(client: OpenAI):
    structured_llm = client.chat.completions.with_structured_output(QueryClassification)

    def _node(state: AssistantState):
        last_message = state["messages"][-1] if state.get("messages") else {"content": ""}
        system_prompt = """
        You are a router for an assistant that can classify user queries into three categories:
        1. excel_insight: Queries that require analytics on Excel logs. The user is looking for insights, statistics, or analysis of the data in the Excel logs.\n
        2. rfi_lookup: Queries that want information on the contents of specific RFIs. The user is looking for specific information tied to information on servers about RFIs.\n
        3. general: General questions that don't fit into the above categories. The user is asking a general question that doesn't require analytics on Excel logs or information about specific RFIs.\n
        Respond only with a JSON object matching the schema.
        """
        response = structured_llm.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": last_message.content}
            ],
            temperature=0,
        )
        state["query_class"] = response.query_class
        return {
            "excel_insight": "generate_code",
            "rfi_lookup": "match_rfis",
            "general": "retrieve_pinecone"
        }[response.query_class]
    return _node
    