# app/graph/nodes/classify.py
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Optional, List
from langchain_openai import ChatOpenAI
from app.graph.state import AssistantState
from app.config import JSON_DESCRIPTION

class QueryClassification(BaseModel):
    query_class: Literal["excel_insight", "rfi_lookup", "building_code_query", "general"] = Field(
        ..., 
        description="Classify if the message requires analytics on Excel, RFI lookup, building code query or is a general question"
    )
    query_subclass: Optional[Literal["needs_llm", "no_llm"]] = Field(
        "needs_llm",
        description="Specify whether the Excel insight query requires LLM-based semantic interpretation ('needs_llm') or can be answered using simple DataFrame operations ('no_llm')"
    )

def classify_query(client: ChatOpenAI):
    structured_llm = client.with_structured_output(QueryClassification)

    def _node(state: AssistantState):
        print("Classifying query...")
        last_message = state.get("rewritten_query", "")

        system_prompt = f"""
        You are a router for an assistant that classifies user queries into two levels:
        A. **query_class**: Primary category of the query
        B. **query_subclass**: Secondary category of the query, only applicable if the query_class is "excel_insight"

        Here are the possible values for each field:
        A **query_class**:
            1. "excel_insight": Queries that involve structured data analysis or retrieval from a tabular dataset. This includes:
                - Summarizing, filtering, counting, grouping, sorting, or computing statistics or time-based metrics
                - Answering questions about specific records, attributes, or entries stored in structured fields
                - Performing analysis using columns such as dates, statuses, categories, comments, IDs, or numerical values
                - If the query can be answered by referencing structured tabular values described in the provided schema, it belongs in this class

            2. **rfi_lookup**: Queries that require accessing or quoting the full document content of a specific RFI, or locating its original folder or file.
            - This includes questions about what a document “says” or requests to "open", "find", or "read" a particular RFI file

            3. **building_code_query**: Queries about AEC codes/standards (e.g., ACI 318, ASCE 7, AWS D1.1, AISC 360/341, NDS, TMS 402/602, IBC/IEBC/ASCE 41, etc.). 
            Heuristics: mentions of "per code", "per ASCE 7-22 §12.8…", "ACI 318-19 Table…", "AWS D1.1 Clause…", "phi, omega, R, C_d", "Sds/S1", load combinations, base shear, UT/RT/MT/VT, CJP/PJP, detailing limits,
            wind/snow/seismic drifts/anchors/diaphragms/collectors, material-specific design criteria (concrete/steel/wood/masonry).

            4. **general**: Any other query unrelated to structured RFI logs or document lookup. These may include questions about company history, projects, scheduling, people, or unrelated topics.
        
        B. **query_subclass** — only applicable if query_class is "excel_insight":
            1. "needs_llm": Use this if the query requires semantic understanding, classification, interpretation of comments, extraction of structured meaning from free text, or complex logic that can't be done by filtering/grouping alone.
              Example: "Classify which RFIs involve design changes or are outside our structural scope."
            2. "no_llm": Use this if the query can be answered through simple pandas operations — like filtering rows, counting, grouping, or sorting by structured fields.
              Example: "How many RFIs were resolved in under 10 business days?"

         You will be given the user's query and a JSON schema of the Excel fields to help make this determination.
        
        Here is the JSON schema describing the fields available in the Excel File:
        {JSON_DESCRIPTION}

        Use this to decide whether the query is answerable from structured Excel data or requires direct access to the document text.

        Respond only with a JSON object matching the schema.
        """
        response = structured_llm.invoke([
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": last_message}
        ])

        state["query_class"] = response.query_class
        state["query_subclass"] = response.query_subclass
        return state
    return _node
    