# File: app/graph/nodes/excel_insight.py
import sys
import io
import re
import json
from typing import Callable
import pandas as pd
#from openai import OpenAI
from langchain_openai import ChatOpenAI
from app.graph.state import AssistantState
from app.config import JSON_DESCRIPTION
from datetime import datetime
import re

def generate_code(client: ChatOpenAI, df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    sample_records = df.head(5).to_dict(orient="records")
    metadata = JSON_DESCRIPTION

    def _node(state: AssistantState) -> AssistantState:
        instruction = state["messages"][-1]["content"] if state.get("messages") else ""

        prompt = f"""
        You are given a pandas DataFrame called `df`.

        - Sample records: {sample_records}
        - Metadata: {json.dumps(metadata)}
        - Task: The user has also provided the following instruction:
        {instruction}

        Write a clean, minimal Python function that:
        - Uses the given `df` directly (DO NOT define or read `df` in your code).
        - Includes all required `import` statements.
        - Handles missing or malformed data gracefully (e.g., use `.dropna()` or `errors='coerce'`).
        - Avoids `SettingWithCopyWarning` (use `.copy()` before modifying slices).
        - Returns or prints clear output (tables, plots, etc.), not just variable assignments.
        - Avoids any file I/O or system access.
        - Executes the function at the end so the result is printed or visualized.
        - DO NOT include sample data, test code, or markdown — only return valid Python code.

        Return ONLY the raw code (no markdown, explanation, or extra text).
        """

        completion = client.invoke([
                {"role": "system", "content": "You are a helpful python data scientist. Use the context to answer clearly and professionally."},
                {"role": "user", "content": prompt.strip()}
        ])
        answer = completion.content.strip()
        clean_code = re.sub(r"^```(?:python)?|```$", "", answer.strip(), flags=re.MULTILINE)
        state["code"] = clean_code
        return state
    return _node

def extract_final_answer(text: str) -> str:
    # Remove leading/trailing whitespace
    text = text.strip()
    pattern = r"=== FINAL ANSWER ===\s*(.*?)\s*=== ANALYSIS ===\s*(.*)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        final_answer = match.group(1).strip()
        analysis = match.group(2).strip()
        return f"=== FINAL ANSWER ===\n{final_answer}\n\n=== ANALYSIS ===\n{analysis}"

    else:
        return text.strip()  # fallback

def execute_code(client: ChatOpenAI, df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        code = state["code"]
        instruction = state["messages"][-1]["content"] if state.get("messages") else ""

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            local_vars = {"df": df}
            exec(code, globals(), local_vars)
            output = redirected_output.getvalue()
        except Exception as e:
            output = f"❌ Error during execution: {str(e)}"
        finally:
            sys.stdout = old_stdout

        state["output"] = output

        # Optionally summarize output via LLM
        prompt = f"""
        The user instruction was: 
        {instruction}

        The following code was executed:
        {code}

        It produced this output:
        {output}

        Return only the following, exactly as formatted:

        === FINAL ANSWER ===
        <clean and readable output from the code, shown as a plain table or list — no markdown>

        === ANALYSIS ===
        <brief insights, issues or observations>

        - DO NOT include any headings like 'Generated Code' or 'Code Output'.
        - DO NOT explain the code.
        - DO NOT reprint the code.
        - DO NOT say anything conversational.
        - Return only the FINAL ANSWER and ANALYSIS sections — nothing else.
        """
        summary = client.invoke([
                {"role": "system", "content": "You are a strict formatter. Only return the FINAL ANSWER and ANALYSIS sections. Do not return any code or markdown. Never include labels like 'Generated Code' or 'Code Output'."},
                {"role": "user", "content": prompt.strip()}
            ])
        answer = extract_final_answer(summary.content.strip())
        state["final_answer"] = answer
        return state
    return _node
