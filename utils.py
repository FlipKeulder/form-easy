from datetime import datetime
import os
import pandas as pd
from PyPDF2 import PdfMerger
from config import EMPLOYEE_CSV, CSV_ENCODING, EVENT_FOLDER

# ──────────────────────────────────────
# 💾 Employee + Event CSV Operations
# ──────────────────────────────────────

# This module handles reading employee data from a CSV file and saving event rows to CSV files.
def read_employees():
    df = pd.read_csv(EMPLOYEE_CSV, encoding=CSV_ENCODING, dtype={"ID Number": str, "Contact": str})
    return df.to_dict(orient="records")

# This function saves event rows to a CSV file named by the event date.
# The date is formatted as YYYYMM, and if the file already exists, it appends
def save_event_rows(rows, event_date):
    try:
        timestamp = datetime.strptime(event_date, "%Y-%m-%d").strftime("%Y%m")
    except ValueError:
        print("Invalid event date format.")
        return
    # Ensure the event folder exists
    filename = os.path.join(EVENT_FOLDER, f"{timestamp}.csv")
    df_new = pd.DataFrame(rows)

    # Create the event folder if it doesn't exist
    if not os.path.exists(filename):
        df_new.to_csv(filename, index=False, encoding=CSV_ENCODING)
    else:
        try:
            existing = pd.read_csv(filename, encoding=CSV_ENCODING)
            df = pd.concat([existing, df_new], ignore_index=True)
        except pd.errors.EmptyDataError:
            df = df_new
        df.to_csv(filename, index=False, encoding=CSV_ENCODING)

# ──────────────────────────────────────
# 📎 PDF Utilities
# ──────────────────────────────────────

# This module provides utilities for merging PDF files and retrieving employer information.
def merge_pdfs(pdf_paths, output_path):
    merger = PdfMerger()
    for path in pdf_paths:
        merger.append(path)
    merger.write(output_path)
    merger.close()

# This function retrieves employer information, which can be used in PDF generation or other contexts.
# It returns a dictionary with the employer's name, address, and contact information.
def get_employer_info():
    return {
        "name": "Form-Easy company",
        "address": "123 Rural Road, Newcastle",
        "contact": "012 345 6789"
    }

# ──────────────────────────────────────
# 🔖 Event ID Helpers
# ──────────────────────────────────────

# These functions encode and decode event IDs based on the event date and name.
# The event ID is a combination of the date and the event name, formatted for easy retrieval
def encode_event_id(date_str, name):
    return f"{date_str}_{name.replace(' ', '_')}"

# This function decodes an event ID back into its date and name components.
# It splits the ID at the first underscore to separate the date from the name.
def decode_event_id(event_id):
    date_part, name_part = event_id.split("_", 1)
    return date_part, name_part.replace("_", " ")