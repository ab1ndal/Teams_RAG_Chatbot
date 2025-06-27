# File: app/read_excel.py
# Author: Abhinav Bindal
# Date: 2025-06-26
# Description: Reads an Excel file and returns a pandas DataFrame

import pandas as pd
import json
from openai import OpenAI
from pathlib import Path
from config import OPENAI_API_KEY
import re
import sys
import io
import matplotlib.pyplot as plt

client = OpenAI(api_key=OPENAI_API_KEY)

file_path = Path("./docs/CCC - CA Log (Current).xlsm")
sheet_name = "RFIs"
header_row = 5
verbose = False
removeCols = ["Overdue Check", "Unnamed: 14", "Backup comments in correct order from Backup File"]
renameCols = {"Unnamed: 1": "Link", 
"Date\nReceived": "Date Received", 
"Date\nRequested": "Date Requested", 
"Date\nSent": "Date Sent"}

json_input = {
  "RFI #": {
    "description": "Unique identifier for each Request for Information (RFI). Follow-up RFIs are denoted using a decimal format (e.g., 0016.1, 0016.2) to indicate continuation of the original RFI.",
    "type": "string (may contain decimal extension for follow-ups)",
    "sample_value": "0016.2"
    },
  "Link": {
    "description": "File path or hyperlink to the associated RFI document or folder",
    "type": "string (file path)",
    "sample_value": "N:\\2019\\19032.BD - Century City JMB Tower\\CA\\RFI's\\Responded\\0016.2"
  },
  "Status": {
    "description": "Current status of the RFI. U = Unanswered, IP = In Progress, W - Arch = Waiting on Architect, W - Contr = Waiting on Contractor, A = Answered",
    "type": "string (categorical)",
    "sample_value": "A"
  },
  "RFI Description": {
    "description": "Brief textual summary of the issue or clarification requested in the RFI",
    "type": "string",
    "sample_value": "STR - TWR - Structural Steel Confirmation per Inquiry Log"
  },
  "Sheet #/Reference": {
    "description": "Drawing sheet number or document reference associated with the RFI (if applicable)",
    "type": "string or null",
    "sample_value": "S5002, S5003"
  },
  "Date Received": {
    "description": "Date the RFI was received by the NYA team",
    "type": "datetime",
    "sample_value": "2022-10-03"
  },
  "Date Requested": {
    "description": "Requested deadline for response to the RFI",
    "type": "datetime",
    "sample_value": "2022-10-10"
  },
  "Date Sent": {
    "description": "Date the response was sent back to the requesting party",
    "type": "datetime or null",
    "sample_value": "2022-10-07"
  },
  "Business Days": {
    "description": "Business days taken between Date Received and Date Sent",
    "type": "integer or null",
    "sample_value": 4
  },
  "Ans. By": {
    "description": "Initials or name of the NYA team member who answered the RFI",
    "type": "string or null",
    "sample_value": "DT"
  },
  "SSK #": {
    "description": "Reference number for associated Supplemental Sketches (if any)",
    "type": "string or null",
    "sample_value": "SSK-001"
  },
  "Internal NYA Comments": {
    "description": "Chronological internal notes about the handling and review of the RFI by the NYA team",
    "type": "string (multi-line text)",
    "sample_value": "10/04/22: Just confirming prior INQ log (only items that had already been addressed) - need to review just to confirm.\n10/07/22: Took a quick review - this was only things that already had responses directly in the INQ log, so good to go, just noted no exceptions."
  }
}

def load_excel(file_path: Path, sheet_name: str, header_row: int, removeCols: list[str], renameCols: dict[str, str], verbose: bool):
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row-1).fillna("")

    # Drop Overdue Check column, Unnamed: 14, Backup comments in correct order from Backup File: column
    df = df.drop(columns=removeCols)

    # Rename Unnamed: 1 to Link
    df = df.rename(columns=renameCols)

    if verbose:
        for k, v in df.iloc[5].to_dict().items():
            print(f"{k}: {v}")
        print(df.columns)
    return df

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

    print("=== Execution Output ===")
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
    print(answer)

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
    df = load_excel(file_path, sheet_name, header_row, removeCols, renameCols, verbose)
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

    





