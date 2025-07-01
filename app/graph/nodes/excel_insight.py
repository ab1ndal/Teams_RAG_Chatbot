# File: app/graph/nodes/excel_insight.py
import sys
import io
import re
import json
from typing import Callable
import pandas as pd
from openai import OpenAI
from app.graph.state import AssistantState
from app.config import JSON_DESCRIPTION

def generate_code(client: OpenAI, df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    sample_records = df.head(5).to_dict(orient="records")
    metadata = JSON_DESCRIPTION

    def _node(state: AssistantState) -> AssistantState:
        instruction = state["messages"][-1].content if state.get("messages") else ""

        prompt = f"""
        The user has provided a pandas dataframe with the following structure:
        - Sample records: {sample_records}
        - Metadata: {json.dumps(metadata)}
        - Task: The user has also provided the following instruction:
        {instruction}

        Write a clean minimal Python function that assumes the dataframe is loaded as 'df'. 
        This will be provided by the user so donot hallucinate this in execution.
        Avoid any file I/O operations that can be dangerous and execute the user task.
        Return the function and call it at the end, so the output is printed or plotted as needed. Do not include markdown or explanation.
        Make sure the result of the task is shown in the output. Do not just return values—ensure something is printed or visualized.
        """

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful python data scientist. Use the context to answer clearly and professionally."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        answer = completion.choices[0].message.content.strip()
        clean_code = re.sub(r"^```(?:python)?|```$", "", answer.strip(), flags=re.MULTILINE)
        state["code"] = clean_code
        return state
    return _node

def execute_code(client: OpenAI, df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        code = state["code"]
        instruction = state["messages"][-1].content if state.get("messages") else ""

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            local_vars = {"df": df}
            exec(code, {}, local_vars)
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
        summary = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful data scientist."},
                {"role": "user", "content": prompt}
            ]
        ).choices[0].message.content.strip()

        state["final_answer"] = summary
        return state
    return _node
