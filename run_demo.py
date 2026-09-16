import csv
import io
import json
from datetime import date, timedelta

from processor import process_file


def main():
    today = date.today()

    rows = [
        {
            "employee_name": "Alice Johnson",
            "employee_email": "alice.johnson@example.com",
            "employee_phone": "555-0101",
            "employee_id": "E-1001",
            "job_role": "Line Cook",
            "work_location": "Downtown",
            "department": "Kitchen",
            "certification_type": "Food Handler Card",
            "certification_number": "FH-99811",
            "issuing_authority": "ServSafe",
            "issue_date": (today - timedelta(days=730)).isoformat(),
            "expiration_date": (today + timedelta(days=120)).isoformat(),
            "renewal_period_months": "36",
            "required_for_role": "true",
            "document_file_name_or_link": "alice_food_handler.pdf",
            "notes": "Renewal not yet scheduled",
        },
        {
            "employee_name": "Marcus Lee",
            "employee_email": "marcus.lee@example.com",
            "employee_phone": "555-0102",
            "employee_id": "E-1002",
            "job_role": "Electrician",
            "work_location": "Riverside",
            "department": "Field",
            "certification_type": "OSHA 30",
            "certification_number": "OSHA-77231",
            "issuing_authority": "OSHA Training Institute",
            "issue_date": (today - timedelta(days=300)).isoformat(),
            "expiration_date": (today + timedelta(days=20)).isoformat(),
            "renewal_period_months": "12",
            "required_for_role": "true",
            "document_file_name_or_link": "marcus_osha.pdf",
            "notes": "",
        },
        {
            "employee_name": "Dana Ortiz",
            "employee_email": "dana.ortiz@example.com",
            "employee_phone": "555-0103",
            "employee_id": "E-1003",
            "job_role": "Site Supervisor",
            "work_location": "Northgate",
            "department": "Construction",
            "certification_type": "First Aid/CPR",
            "certification_number": "CPR-55121",
            "issuing_authority": "Red Cross",
            "issue_date": (today - timedelta(days=800)).isoformat(),
            "expiration_date": (today - timedelta(days=5)).isoformat(),
            "renewal_period_months": "24",
            "required_for_role": "true",
            "document_file_name_or_link": "dana_cpr.pdf",
            "notes": "Needs immediate renewal",
        },
        {
            "employee_name": "Noah Williams",
            "employee_email": "noah.williams@example.com",
            "employee_phone": "555-0104",
            "employee_id": "E-1004",
            "job_role": "Dishwasher",
            "work_location": "Downtown",
            "department": "Kitchen",
            "certification_type": "",
            "certification_number": "",
            "issuing_authority": "",
            "issue_date": "",
            "expiration_date": "",
            "renewal_period_months": "",
            "required_for_role": "true",
            "document_file_name_or_link": "",
            "notes": "Required food handler card missing",
        },
        {
            "employee_name": "Priya Shah",
            "employee_email": "priya.shah@example.com",
            "employee_phone": "555-0105",
            "employee_id": "E-1005",
            "job_role": "Childcare Teacher",
            "work_location": "Sunset Center",
            "department": "Classroom",
            "certification_type": "Background Check",
            "certification_number": "BG-88112",
            "issuing_authority": "State Licensing",
            "issue_date": (today - timedelta(days=100)).isoformat(),
            "expiration_date": "",
            "renewal_period_months": "24",
            "required_for_role": "true",
            "document_file_name_or_link": "priya_background_check.pdf",
            "notes": "No expiration date provided",
        },
    ]

    fieldnames = list(rows[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    results = process_file(buffer.getvalue().encode("utf-8"))

    assert isinstance(results, list)
    assert len(results) == len(rows)

    required_keys = {"title", "status", "details", "due_date"}
    for record in results:
        assert required_keys.issubset(record.keys())
        assert isinstance(record["details"], dict)
        assert isinstance(record["due_date"], str) or record["due_date"] is None

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
