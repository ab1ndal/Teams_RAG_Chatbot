# app/graph/nodes/classify.py
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Optional, List
from langchain_openai import ChatOpenAI
from app.graph.state import AssistantState
from app.config import JSON_DESCRIPTION
from app.utils import helper

class ClassifyAndRewrite(BaseModel):
    query_class: Literal["excel_insight", "rfi_lookup", "building_code_query", "general"] = Field(
        ..., 
        description="Classify if the message requires analytics on Excel, RFI lookup, building code query or is a general question"
    )
    query_subclass: Optional[Literal["needs_llm", "no_llm"]] = Field(
        "needs_llm",
        description="Specify whether the Excel insight query requires LLM-based semantic interpretation ('needs_llm') or can be answered using simple DataFrame operations ('no_llm')"
    )
    rewritten: Optional[str] = Field(
        None,
        description="A concise, retrieval-ready reformulation that preserves all acronyms, editions, and section/table/figure numbers."
    )

def classify_and_rewrite_query(client: ChatOpenAI):
    structured_llm = client.with_structured_output(ClassifyAndRewrite)

    def _node(state: AssistantState) -> AssistantState:
        if state.get("error") or not state.get("guardrails", {}).get("allowed", True):
            return state

        print("Classifying and rewriting query...")
        previous_rewrites = "\n".join(state.get("previous_rewrites", []))

        user_query_raw = helper._last_user_text(state["messages"])
        general_suffix = f"""----------------
            Current Summary (may be "(none)"):
            {state.get('history', '(none)')}
            Recent turns:
            {helper.render_message_summary(state['messages'], window_size=5)}
            ----------------
            Previous rewritten queries (if any):
            {previous_rewrites}
            ----------------
            Original query: {user_query_raw}
            """

        system_prompt = f"""
        You are a router for an internal AEC assistant. You have the following tasks:
        
        1) Rewrite the user query into a precise, self-contained form that is directly suitable for both document retrieval and structured data analysis.
           - Incorporate relevant context from prior conversation (Summary, Recent turns, Previous rewritten queries) turns to resolve ambiguities in continuation queries.
           - Retain all technical terms, variable names, and acronyms exactly as written (do not expand or normalize them).
           - Preserve specific details that may be important for code generation, standards lookup, or statistical analysis.
           - Expand vague references into explicit phrasing when context allows (e.g., replace “these values” with “drift ratios from ASCE 7-22 Table 12.12-1” or “RFI close dates” if identifiable).
           - For data analysis queries, ensure the rewritten query highlights operations (filter, group, count, compute, plot, compare) and the fields/metrics they apply to.
           - Ensure the rewritten query remains faithful to the user’s original intent while improving clarity, precision, and downstream suitability.
        2) Classify the REWRITTEN user query into two levels:
        A. **query_class**: Primary category of the query
        B. **query_subclass**: Secondary category of the query, only applicable if the query_class is "excel_insight"

        Here are the possible values for each field:
        A **query_class**:
            1. "excel_insight": Queries that involve structured data analysis or retrieval from a tabular dataset. This includes plotting, summarizing, filtering, counting, grouping, sorting, or computing statistics or time-based metrics.

            2. **rfi_lookup**: Queries that includes finding/quoting/opening specific RFIs or their source files. Heuristics: What does RFI xxx say..?

            3. **building_code_query**: Queries about AEC codes/standards (e.g., ACI 318, ASCE 7, AWS D1.1, AISC 360/341, NDS, TMS 402/602, IBC/IEBC/ASCE 41, etc.). 
            Heuristics: mentions of "per code", "per ASCE 7-22 §12.8…", "ACI 318-19 Table…", "AWS D1.1 Clause…", "phi, omega, R, C_d", "Sds/S1", load combinations, base shear, UT/RT/MT/VT, CJP/PJP, detailing limits,
            wind/snow/seismic drifts/anchors/diaphragms/collectors, material-specific design criteria (concrete/steel/wood/masonry).

            4. **general**: Any other query unrelated to other queries. These may include questions about company history, projects, scheduling, people, or unrelated topics.
        
        B. **query_subclass** — only applicable if query_class is "excel_insight":
            1. "needs_llm": Use this if the query requires semantic understanding, classification, interpretation of comments, extraction of structured meaning from free text, or complex logic that can't be done by filtering/grouping alone.
              Example: "Classify which RFIs involve design changes or are outside our structural scope."
            2. "no_llm": Use this if the query can be answered through simple pandas operations — like filtering rows, counting, grouping, or sorting by structured fields.
              Example: "How many RFIs were resolved in under 10 business days?"

        Use this to decide whether the query is answerable from structured Excel data or requires direct access to the document text.

        Respond only with a JSON object matching the schema.
        """

        user_query = f"""Rewrite the original query based on Recent turns (if ambiguous) and Current Summary. Make it more precise and suitable for document retrieval. DO NOT replace any acronyms.
        After re-writing the query, classify it into two levels:
        A. **query_class**: Primary category of the query
        B. **query_subclass**: Secondary category of the query, only applicable if the query_class is "excel_insight"
        {general_suffix}
        """

        response = structured_llm.invoke([
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_query}
        ])

        state["query_class"] = response.query_class
        state["query_subclass"] = response.query_subclass
        state["rewritten_query"] = response.rewritten
        print(state["previous_rewrites"])
        state["previous_rewrites"].append(response.rewritten)
        state["previous_rewrites"] = state["previous_rewrites"][-10:]
        print(state["previous_rewrites"])
        rewrites_str = "']['".join(state["previous_rewrites"])
        rewrites_str = f"[{rewrites_str}]"
        state["previous_rewrites"] = rewrites_str

        return state
    return _node
    