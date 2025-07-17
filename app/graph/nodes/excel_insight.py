# File: app/graph/nodes/excel_insight.py
import sys
import io
import re
import json
from typing import Callable, List, Literal
import pandas as pd
from langchain_openai import ChatOpenAI
from app.graph.state import AssistantState
from app.config import JSON_DESCRIPTION
from datetime import datetime
import ast
from pandas import Timestamp, NaT, ExcelWriter
from io import BytesIO
import asyncio
import matplotlib.pyplot as plt
import fuzzywuzzy


def generate_code(client: ChatOpenAI, df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    sample_records = df.head(5).to_dict(orient="records")
    metadata = JSON_DESCRIPTION

    def _node(state: AssistantState) -> AssistantState:
        instruction = state["messages"][-1]["content"] if state.get("messages") else ""

        if state.get("query_class") == "rfi_lookup":
            instruction += """
            The user is looking for information about specific RFIs.
            Return all information about the RFIs that match the user's query from the dataframe in form of list of dictionaries.
            """
            
        if state.get("query_subclass") == "no_llm":
            prompt = f"""
            You are given a pandas dataframe called `df`
            Context:
            - Sample records: {sample_records}
            - Metadata: {json.dumps(metadata)}

            Your job is to write a **clean, minimal Python function** that performs the following user-defined task:
            {instruction}

            FOLLOW THE GUIDELINES EXACTLY BELOW. NO DEVIATIONS ARE ALLOWED.

            GUIDELINES:
            - Use the provided `df` directly. DO NOT redefine, re-import, or reload it.
            - Use only modern pandas (v2.3.0+) methods. DO NOT use deprecated methods like `.append()` or `.ix`.
            - Use `.copy()` before modifying any filtered DataFrame to avoid `SettingWithCopyWarning`.
            - Handle missing or malformed data gracefully (e.g., with `.dropna()`, `.fillna()`, or `errors='coerce'`).
            - Include all required imports (`pandas`, `openpyxl`, etc.) at the top of the script.
            - If the task involves saving, visualizing, or printing results, ensure those are clearly produced.
            - Ensure the final result is printed using print(...) — do not rely on return values alone.
            - Ensure that the function is run with the provided `df` argument.
            
            Strict Output Rule:
            Return ONLY valid, executable Python code. Do not include markdown, explanations, sample data, or test code.
            """
        else:
            prompt = f"""
            You are given the following. These will be passed to the function at runtime as arguments.

            - A pandas DataFrame named `df` that is already defined and contains tabular data.
            - A `client` instance of `ChatOpenAI` from `langchain_openai`, already initialized and passed in. DO NOT import, define or reinitialize it.

            Your job is to write a **clean, minimal Python function** that performs the following user-defined task:
            {instruction}

            FOLLOW THE GUIDELINES EXACTLY BELOW. NO DEVIATIONS ARE ALLOWED.

            Context:
            - Sample records: {sample_records}
            - Metadata: {json.dumps(metadata)}

            Guidelines:
            - Use the provided `df` directly. DO NOT redefine, re-import, or reload it.
            - If semantic interpretation, classification, question answering, or structured extraction is needed, use the `client`.
            - If multiple rows require semantic classification, use `asyncio.gather()` to process them concurrently.
            - Use a concurrency control pattern like `semaphore = asyncio.Semaphore(5)` to rate-limit concurrent LLM calls.
            - Define an async helper like:

                async def classify_row(row):
                    async with semaphore:
                        messages = [
                            {{ "role": "system", "content": "You are an expert assistant that classifies RFIs." }},
                            {{ "role": "user", "content": f"Classify this RFI:\\nDescription: {{row['RFI Description']}}\\nComments: {{row['Internal NYA Comments']}}" }}
                        ]
                        response = await client.ainvoke(messages)
                        return response.content.strip()

            - Then call:
                results = await asyncio.gather(*[classify_row(row) for _, row in unclassified_df.iterrows()])

            - Assign the results back to the DataFrame, row by row.
            - Use only modern pandas (v2.3.0+) methods. DO NOT use deprecated methods like `.append()` or `.ix`.
            - Use `.copy()` before modifying any filtered DataFrame to avoid `SettingWithCopyWarning`.
            - Handle missing or malformed data gracefully (e.g., with `.dropna()`, `.fillna()`, or `errors='coerce'`).
            - Wrap the main logic in `async def` and call it using `asyncio.run(...)` at the end.
            - Include all required imports (`pandas`, `asyncio`, `openpyxl`, etc.) at the top of the script.
            - If the task involves saving, visualizing, or printing results, ensure those are clearly produced.
            - DO NOT access `response['choices']` or `response['message']`. Use `response.content`.
            - Ensure the final result is printed using print(...) — do not rely on return values alone.
            
            Strict Output Rule:
            Return ONLY valid, executable Python code. Do not include markdown, explanations, sample data, or test code.
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
    pattern = r"=== CODE ===\s*(.*?)\s*=== FINAL ANSWER ===\s*(.*?)\s*=== ANALYSIS ===\s*(.*)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1).strip()
        final_answer = match.group(2).strip()
        analysis = match.group(3).strip()
        return f"=== CODE ===\n{code}\n\n=== FINAL ANSWER ===\n{final_answer}\n\n=== ANALYSIS ===\n{analysis}"

    else:
        return text.strip()  # fallback

def execute_code(client: ChatOpenAI, df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        code = state["code"]
        instruction = state["messages"][-1]["content"] if state.get("messages") else ""

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            local_vars = {"df": df, "client": client}
            exec(code, local_vars)
            output = redirected_output.getvalue()
        except Exception as e:
            output = f"❌ Error during execution: {str(e)}"
        finally:
            sys.stdout = old_stdout

        state["output"] = output

        if state.get("query_class") == "rfi_lookup":
            data_str_clean = output.replace("Timestamp(", "").replace(")", "").replace("NaT", "None")
            state["rfi_matches"] = ast.literal_eval(data_str_clean)
            return state

        
        prompt = f"""
            The user instruction was: 
            {instruction}

            The following code was executed:
            {code}

            It produced this output:
            {output}

            Return only the following, exactly as formatted:

            === CODE ===
            <the code that was executed>

            === FINAL ANSWER ===
            <clean and readable output from the code, shown as a plain table or list>

            === ANALYSIS ===
            <brief explanation of the method used>
            <brief insights, issues, assumptions, or observations>

            Guidelines:
            - DO NOT return markdown or bullets.
            - Provide a concise paragraph that summarizes the approach and what the code is doing.
            - If applicable, highlight any assumptions, possible issues, or the reasoning behind using specific methods.
            - DO NOT say anything conversational.
            - Return only the FINAL ANSWER, ANALYSIS, and CODE sections — nothing else.
        
            Example:
            === CODE ===
            print("hello")

            === FINAL ANSWER ===
            hello

            === ANALYSIS ===
            This code prints a greeting. No input/output issues expected.
        """

        summary = client.invoke([
                {"role": "system", "content": "You are a strict formatter. Only return the FINAL ANSWER, ANALYSIS and CODE sections. Do not return any markdown."},
                {"role": "user", "content": prompt.strip()}
            ])
        answer = extract_final_answer(summary.content.strip())
        state["final_answer"] = answer
        return state
    return _node
