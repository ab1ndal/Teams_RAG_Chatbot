# File: app/read_excel.py
# Author: Abhinav Bindal
# Date: 2025-06-26
# Description: Reads an Excel file and returns a pandas DataFrame

import pandas as pd
import json
from pathlib import Path
import re
import sys
import io
import matplotlib.pyplot as plt
from config import JSON_DESCRIPTION, EXCEL_PATH, REMOVE_COLS, RENAME_COLS, SHEET_NAME, HEADER_ROW
from app.services.excel_cache import get_excel_dataframe
from clients.openAI_client import get_client

client = get_client()

file_path = EXCEL_PATH
sheet_name = SHEET_NAME
header_row = HEADER_ROW
verbose = False
removeCols = REMOVE_COLS
renameCols = RENAME_COLS

json_input = JSON_DESCRIPTION

def execute_code(code, df, user_instruction):
    # Redirect stdout to capture print output
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        local_vars = {"df": df}
        exec(code, globals(), local_vars)
        output = redirected_output.getvalue()
    finally:
        sys.stdout = old_stdout  # Restore original stdout

    #print("=== Execution Output ===")
    prompt = f"""
    The user has provided the following instruction:
    {user_instruction}
    
    The following code was executed:
    {code}
    
    The following output was produced:
    {output}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful python data scientist. Use the context to answer clearly and professionally."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    answer = response.choices[0].message.content.strip()
    #print(answer)

def generate_code(df: pd.DataFrame, metadata: json, user_instruction: str):
    sample_records = df.head(5).to_dict(orient="records")
    prompt = f"""
    The user has provided a pandas dataframe with the following structure:
    - Sample records: {sample_records}
    - Metadata: {metadata}
    - Task: The user has also provided the following instruction:
    {user_instruction}

    Write a clean minimal Python function that assumes the dataframe is loaded as 'df'. This will be provided by the user so donot hallucinate this in execution.
    Avoid any file I/O operations that can be dangerous and execute the user task.
    Return the function and call it at the end, so the output is printed or plotted as needed. Do not include markdown or explanation.
    Make sure the result of the task is shown in the output. Do not just return values—ensure something is printed or visualized.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful python data scientist. Use the context to answer clearly and professionally."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    answer = response.choices[0].message.content.strip()
    clean_code = re.sub(r"^```(?:python)?|```$", "", answer.strip(), flags=re.MULTILINE)
    return clean_code

if __name__ == "__main__":
    df = get_excel_dataframe(file_path, sheet_name, header_row, removeCols, renameCols, verbose)
    metadata = json_input
    #user_instruction = "Show me information about RFI 0026."
    #user_instruction = "Show me the RFI #s that have not been answered. Give me the total count, RFI title and when they were received"
    #user_instruction = "Show me number of RFIs that I received every month. Give me the response in the following format:Month, Year - Count of RFIs"
    #user_instruction = "What is the average turn around time for RFIs for the month of March 2023?"
    user_instruction = "Categeorize RFIs based on title of the RFI. Tell me type of RFIs and count of RFIs for each type"
    user_instruction = "Split the RFIs into categories based by name. Now create me a pie chart with number of RFIs in each category. Format the Pie Chart beautifully"
    user_instruction = "Show me all RFIs related to Walls. Give me RFI#: RFI Title"
    code = generate_code(df, metadata, user_instruction)
    #print(code)
    execute_code(code, df, user_instruction)

    





