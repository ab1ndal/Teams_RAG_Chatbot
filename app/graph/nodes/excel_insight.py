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
                {"role": "user", "content": prompt}
        ])
        answer = completion.content.strip()
        clean_code = re.sub(r"^```(?:python)?|```$", "", answer.strip(), flags=re.MULTILINE)
        state["code"] = clean_code
        return state
    return _node

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
        The user has provided the following instruction: 
        {instruction}
        The following code was executed:
        {code}
        The following output was produced:
        {output}
        """
        summary = client.invoke([
                {"role": "system", "content": "You are a helpful data scientist."},
                {"role": "user", "content": prompt}
            ])
        answer = summary.content.strip()

        state["final_answer"] = answer
        return state
    return _node
