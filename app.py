# ────────────────────────────────────────────────
# 📦 External Libraries
# ────────────────────────────────────────────────
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, make_response, send_file
)
# for PDF generation, copilot helped me understand how to use WeasyPrint
# and Jinja2 for rendering HTML templates to PDF.
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

import pandas as pd
import json
import os
import tempfile
import sys
import io

# ────────────────────────────────────────────────
# 🛠️ Internal Modules
# ────────────────────────────────────────────────
from config import EMPLOYEE_CSV, EVENT_FOLDER, CSV_ENCODING
from utils import (
    read_employees, save_event_rows,
    get_employer_info, encode_event_id
)

# ────────────────────────────────────────────────
# 🧠 Jinja2 Setup (for multipage PDF rendering)
# ────────────────────────────────────────────────
env = Environment(loader=FileSystemLoader("templates"))

# ────────────────────────────────────────────────
# ⚙️ Flask App Configuration
# ────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates")
# I struggled with posting data and after some trial and error,
# Copilot suggested to use a secret key for session management.
# This is essential for securely signing the session cookie.
app.secret_key = "123456789"  # Replace with secure key in production

# ────────────────────────────────────────────────
# 📥 Utility: Load Employee CSV
# ────────────────────────────────────────────────
# I decided to create utility functions to load the CSV's and data,
# so I can reuse it across different routes without duplicating code.
def load_employees():
    try:
        return pd.read_csv(EMPLOYEE_CSV, dtype={"Contact": str})
    except FileNotFoundError:
        return pd.DataFrame(columns=["ID Number", "Surname", "Name", "Contact"])

def load_data():
    return pd.read_csv(EMPLOYEE_CSV, encoding=CSV_ENCODING)

# ───────────────────────────────────────────────
# 👥 Employee Management
# ───────────────────────────────────────────────

# 🏠 Home Page
@app.route("/")
def home():
    return render_template("home.html")

# 📋 Employee Dashboard
@app.route("/employees")
def employees():
    return render_template("employees.html")

# ➕ Add a New Employee
# I struggled with posting data and after some trial and error,
# Copilot suggested to strip the input values to avoid leading/trailing spaces.
# It also helped me understand how to validate the ID number and contact fields.
@app.route("/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        id_number = request.form.get("id_number", "").strip()
        surname = request.form.get("surname", "").strip()
        name = request.form.get("name", "").strip()
        contact = request.form.get("contact", "").strip()
        df = load_data()

        # ✋ Validation checks
        if id_number in df["ID Number"].astype(str).values:
            error = "An employee with this ID number already exists."
        elif not id_number.isdigit() or len(id_number) != 13:
            error = "ID number must be a 13-digit number."
        elif not contact.isdigit() or len(contact) < 10:
            error = "Contact must be at least 10 digits."
        else:
            # ✅ Add new entry to DataFrame
            new_entry = pd.DataFrame([{
                "ID Number": id_number,
                "Surname": surname,
                "Name": name,
                "Contact": contact
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(EMPLOYEE_CSV, index=False)
            session["success"] = "Employee added successfully!"
            return redirect(url_for("add_employee"))

        return render_template("employees/add_employee.html", error=error)

    success = session.pop("success", None)
    return render_template("employees/add_employee.html", success=success)

# ✏️ Edit Employee Record
# this is simple and straightforward, I wanted to load the employee data
# and pre-fill the form fields, so the user can edit existing records.
@app.route("/edit_employee")
def edit_employee():
    df = load_data()
    all_employees = df.sort_values("Surname").to_dict(orient="records")
    selected = None

    # 🎯 Load selected employee by ID
    if id_number := request.args.get("id_number"):
        match = df[df["ID Number"].astype(str) == str(id_number)].to_dict("records")
        if match:
            selected = match[0]

    return render_template(
        "employees/edit_employee.html",
        all_employees=all_employees,
        selected_employee=selected,
        success_message=session.pop("success", None)
    )

# 🔄 Update Employee Details
# I struggled with the logic here, as I wanted to overwrite existing fields
# without adding new rows. Copilot helped me understand how to use `loc` to update
# Copilot also explained what and how jasonify works, so I could return JSON responses.
@app.route("/update_employee", methods=["POST"])
def update_employee():
    df = load_data()
    id_number = request.form.get("id_number")

    if id_number not in df["ID Number"].astype(str).values:
        return jsonify({"error": "Employee not found"}), 404

    # ✍️ Overwrite existing fields
    df.loc[df["ID Number"].astype(str) == id_number, ["Surname", "Name", "Contact"]] = [
        request.form.get("surname"),
        request.form.get("name"),
        request.form.get("contact")
    ]
    df.to_csv(EMPLOYEE_CSV, index=False)
    session["success"] = "Update successful!"
    return redirect(url_for("edit_employee", id_number=id_number))

# ❌ Remove Employee from Dataset
@app.route("/remove_employee", methods=["GET", "POST"])
def remove_employee():
    df = load_data()

    if request.method == "POST":
        id_number = request.form.get("id_number")
        if not id_number or id_number not in df["ID Number"].astype(str).values:
            session["error"] = "Employee not found!"
            return redirect(url_for("remove_employee"))

        # 🧹 Remove employee row
        df = df[df["ID Number"].astype(str) != str(id_number)]
        df.to_csv(EMPLOYEE_CSV, index=False)
        # The success message flashes too quickly, so I store it in the session.
        session["success"] = "Employee removed successfully!"
        return redirect(url_for("remove_employee"))

    return render_template(
        "employees/remove_employee.html",
        all_employees=df.sort_values("Surname").to_dict(orient="records"),
        error=session.pop("error", None),
        success=session.pop("success", None)
    )

# ────────────────────────────────────────────────
# 📅 Event Management
# ────────────────────────────────────────────────

# 🗓️ Create or View Events
# So i have already done a deep dive into json with Copilot,
# and it suggested using JSON to store employee IDs for event assignments.
# This was a significant improvement over my initial approach of using a simple string
# and enabled me to allow other dropdown lists to be populated dynamically based on the selected event.
@app.route("/events", methods=["GET", "POST"])
def events():
    all_employees = sorted(read_employees(), key=lambda e: e["Surname"])

    if request.method == "POST":
        event_name = request.form.get("eventName", "").strip()
        event_date = request.form.get("eventDate", "").strip()
        amount_raw = request.form.get("amountPayable", "0").strip()
        assigned_ids_raw = request.form.get("assignedEmployees", "[]")

        # 🧮 Validate amount
        # I wanted to ensure the amount is a valid float and round it to 2 decimal places,
        # so Copilot suggested using `round(float(amount_raw), 2)`.
        try:
            amount = round(float(amount_raw), 2)
        except (ValueError, TypeError):
            session["error"] = "Amount must be a valid number!"
            return redirect(url_for("events"))

        # 🧾 Validate employee selection
        # I wanted to ensure the assigned IDs are valid JSON,
        # so Copilot suggested using `json.loads` to parse the string.
        try:
            assigned_ids = json.loads(assigned_ids_raw)
        except json.JSONDecodeError:
            session["error"] = "Employee selection is invalid!"
            return redirect(url_for("events"))

        if not event_name or not event_date or not assigned_ids:
            session["error"] = "Complete all fields and assign at least one employee."
            return redirect(url_for("events"))

        # 🧷 Build rows to save
        # I had some issues with the CSV writer not handling floats correctly,
        # so we format the amount as a string with 2 decimal places, Copilot assisted with this.
        formatted_amount = f"{amount:.2f}"
        rows = [
            {
                "Event Name": event_name,
                "Date": event_date,
                "Amount Payable": formatted_amount,
                "Employee ID": emp["ID Number"],
                "Name": emp["Name"],
                "Surname": emp["Surname"],
                "Contact": emp["Contact"]
            }
            for emp_id in assigned_ids
            for emp in all_employees
            if str(emp["ID Number"]).strip() == str(emp_id).strip()
        ]

        save_event_rows(rows, event_date)
        session["success"] = "Event saved successfully!"
        return redirect(url_for("events"))

    return render_template("events.html", all_employees=all_employees)

# ────────────────────────────────────────────────
# 📊 Forms & Document Generation
# ────────────────────────────────────────────────

# 📄 forms Dashboard
@app.route("/forms")
def forms():
    try:
        df = pd.read_csv(EMPLOYEE_CSV, dtype={"Contact": str})
    except FileNotFoundError:
        df = pd.DataFrame(columns=["ID Number", "Surname", "Name", "Contact"])
    employees = df.sort_values("Surname").to_dict(orient="records")
    return render_template("forms.html", all_employees=employees)


# 🧾 Generate Individual Employee PDF for an Event
@app.route("/generate-employee-pdf/<employee_id>/<event_date>")
def generate_employee_pdf(employee_id, event_date):
    
    # Fetch employee data
    employee = next(
        (e for e in read_employees() if str(e["ID Number"]) == employee_id),
        None
    )
    if not employee:
        return "Employee not found", 404

    # Determine CSV file based on event date
    # This was a bit tricky, as we need to extract the month from the date and build the file path,
    # so we use string slicing to get the year and month, and then construct the path.
    # Copilot helped with the string formatting, and os.path.join for the file path.
    month_key = f"{event_date[:4]}{event_date[5:7]}"
    csv_path = os.path.join(EVENT_FOLDER, f"{month_key}.csv")
    if not os.path.exists(csv_path):
        return "No event data for this date", 404

    df = pd.read_csv(csv_path, dtype=str)

    # Apply map was suggested by Copilot to strip whitespace from all string fields,
    # which is essential for matching employee IDs and event dates.
    # This ensures that we don't have leading/trailing spaces causing mismatches.
    # The lambda function checks if the value is a string before stripping it.
    # This was a great learning moment, as I didn't know about `applymap` before.
    # It allows us to apply a function to each element in the DataFrame.
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Match event row
    event_row = df[
        (df["Employee ID"] == employee_id.strip()) &
        (df["Date"] == event_date.strip())
    ]
    if event_row.empty:
        return "No event match for employee on that date", 404

    # iloc[0] is used to get the first row of the DataFrame,
    # as we expect only one match for a given employee and date.
    row = event_row.iloc[0]
    event = {
        "Name": row["Event Name"],
        "Date": row["Date"],
        "AmountPayable": f"{float(row['Amount Payable']):.2f}"
    }

    # Get employer info to inject into all templates
    employer = get_employer_info()

    # List of form templates to render
    # This was a fun part, as I wanted to render multiple templates into a single PDF,
    # so Copilot suggested using Jinja2's Environment to load and render multiple templates.
    # I also learned how to use WeasyPrint to convert HTML to PDF.
    templates = [
        "forms/employment_agreement.html",
        "forms/wage_claim.html",
        "forms/payment_acknowledgment.html"
    ]

    # Render first template
    doc = HTML(string=env.get_template(templates[0]).render(
        employee=employee, event=event, employer=employer)).render()

    # Append the rest
    for tpl in templates[1:]:
        sub = HTML(string=env.get_template(tpl).render(
            employee=employee, event=event, employer=employer)).render()
        doc.pages.extend(sub.pages)

    # Generate response with embedded filename
    filename = f"{employee['Surname']}_{employee['Name']}_{event['Date'].replace('-', '')}.pdf"
    response = make_response(doc.write_pdf())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={filename}"
    return response
    
# 📅 Available Event Months
@app.route("/get-months")
def get_months():
    try:
        files = os.listdir(EVENT_FOLDER)
        months = sorted([
            f.removesuffix(".csv")
            for f in files if f.endswith(".csv") and f.removesuffix(".csv").isdigit()
        ], reverse=True)
        return jsonify(months=months)
    except Exception as e:
        print("Error listing event files:", e)
        return jsonify(months=[])


# 📆 Events Within a Month
@app.route("/get-events/<month>")
def get_events(month):
    try:
        df = pd.read_csv(os.path.join(EVENT_FOLDER, f"{month}.csv"), dtype=str)

        # Group by Event Name + Date and sort by Date DESC
        grouped = (
            df.groupby(["Event Name", "Date"])
              .size()
              .reset_index()
              .sort_values(by="Date", ascending=False)
        )

        return jsonify(events=[
            {
                "name": row["Event Name"],
                "date": row["Date"],
                "id": encode_event_id(row["Date"], row["Event Name"])
            }
            for _, row in grouped.iterrows()
        ])
    except Exception as e:
        print(f"Error loading events for {month}:", e)
        return jsonify(events=[])


# 👥 Employees Assigned to Selected Event
@app.route("/get-employees-in-event/<month>/<event_id>")
def get_employees_in_event(month, event_id):
    try:
        event_date, raw_name = event_id.split("_", 1)
        event_name = raw_name.replace("_", " ")
        path = os.path.join(EVENT_FOLDER, f"{month}.csv")

        df = pd.read_csv(path, dtype=str)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        matches = df[(df["Event Name"] == event_name) & (df["Date"] == event_date)]

        employees = [
            {
                "id": row["Employee ID"],
                "name": row["Name"],
                "surname": row["Surname"]
            }
            for _, row in matches.iterrows()
        ]

        return jsonify(employees=employees)

    # i had to add this exception handling,
    # as sometimes the file might not exist or the data might be malformed.
    except Exception as e:
        print(f"Error fetching employees for '{event_id}' in {month}:", e)
        return jsonify(employees=[])


# ────────────────────────────────────────────────
# 📅 Reports 
# ────────────────────────────────────────────────

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/reports/date")
def report_by_date():
    return render_template("reports/by_date.html")

@app.route("/reports/employee")
def report_by_employee():
    return render_template("reports/by_employee.html")


@app.route("/reports/event")
def report_by_event():
    return render_template("reports/by_event.html")

# 📁 List Available Monthly Files (for dropdown)
@app.route("/get-csv-files")
def get_csv_files():
    folder = os.path.join("data", "events")
    if not os.path.exists(folder):
        return jsonify({"files": []})

    files = [
        f for f in os.listdir(folder)
        if f.endswith(".csv") and f.removesuffix(".csv").isdigit()
    ]
    return jsonify({"files": sorted(files, reverse=True)})

# 📄 Load All Data from File (Sorted Ascending by Date)
@app.route("/report/render/all/<filename>")
def render_full_month_sorted(filename):
    path = os.path.join("data", "events", filename)
    if not os.path.isfile(path):
        return jsonify([])

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip() 

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date", ascending=True)

    return df.to_dict(orient="records")

# 📄 Export Full Month Data as PDF
@app.route("/report/pdf/month/<filename>")
def export_month_pdf(filename):
    path = os.path.join("data", "events", filename)
    if not os.path.isfile(path):
        return "File not found", 404

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date", ascending=True)

    total = df["Amount Payable"].sum()

    rendered = render_template(
        "reports/by_date.html",
         rows=df.to_dict(orient="records"),
         total=total,
         export_mode=True
    )
    pdf = HTML(string=rendered).write_pdf()

    # Use BytesIO to send PDF as a file response and download it.
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        download_name=filename.replace(".csv", "_by_date.pdf"),
        as_attachment=True
    )

# 📄 Render Events by Employee
@app.route("/report/pdf/employee/<filename>")
def export_employee_pdf(filename):
    path = os.path.join("data", "events", filename)
    if not os.path.isfile(path):
        return "File not found", 404

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values(["Surname", "Name", "Date"])

    total = df["Amount Payable"].sum()

    rendered = render_template(
        "reports/by_employee.html",
        rows=df.to_dict(orient="records"),
        total=total,
        export_mode=True
    )
    pdf = HTML(string=rendered).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        download_name=filename.replace(".csv", "_by_employee.pdf"),
        as_attachment=True
    )

# 📄 Render Events by Event
@app.route("/report/pdf/event/<filename>")
def export_event_pdf(filename):
    path = os.path.join("data", "events", filename)
    if not os.path.isfile(path):
        return "File not found", 404

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values(["Event Name", "Date"])

    total = df["Amount Payable"].sum()

    rendered = render_template(
        "reports/by_event.html",
        rows=df.to_dict(orient="records"),
        total=total,
        export_mode=True
    )
    pdf = HTML(string=rendered).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        download_name=filename.replace(".csv", "_by_event.pdf"),
        as_attachment=True
    )

# ⚙️ Launch Flask Development Server
if __name__ == "__main__":
    app.run(debug=True)