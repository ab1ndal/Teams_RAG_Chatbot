import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "test")


# Excel Config
EXCEL_PATH = Path(os.getenv("EXCEL_PATH"))
REMOVE_COLS = [
    "Total Days",
    "Priority",
    #"Overdue Check", 
    #"Unnamed: 14", 
    #"Backup comments in correct order from Backup File"
]
RENAME_COLS = {
    #"Unnamed: 1": "Link",
    "L": "Link", 
    "Date\nReceived": "Date Received", 
    "Date\nRequested": "Date Requested", 
    "Date\nSent": "Date Sent"
}
SHEET_NAME = "RFIs"
HEADER_ROW = 11 #5
USECOLS = "A:N"

JSON_DESCRIPTION = {
  "RFI #": {
    "description": "Unique identifier for each Request for Information (RFI). Follow-up RFIs are denoted using a decimal format (e.g., 0016.1, 0016.2) to indicate continuation of the original RFI.",
    "type": "string (may contain decimal extension for follow-ups)",
    "sample_value": "0016.2"
    },
  "Link": {
    "description": "File path or hyperlink to the associated RFI document or folder. This is the location where RFI is saved on the network drive.",
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
  "Ball in Court": {
    "description": "Initials or name of the NYA team members who are working on the RFI",
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
