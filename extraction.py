import io
import json
import os
import csv
import re

from openai import OpenAI

FIELDS = [
    "employee_name",
    "employee_email",
    "employee_phone",
    "employee_id",
    "job_role",
    "work_location",
    "department",
    "certification_type",
    "certification_number",
    "issuing_authority",
    "issue_date",
    "expiration_date",
    "renewal_period_months",
    "required_for_role",
    "document_file_name_or_link",
    "notes",
    "manager_name",
    "manager_email",
    "hire_date",
    "cert_template_id",
    "verification_status",
    "last_reminder_sent_at",
    "source_document_name",
]

def _strip_code_fences(content):
    content = content.strip()
    fence = chr(96) * 3
    if content.startswith(fence):
        content = content[len(fence):].strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()
        if content.endswith(fence):
            content = content[: -len(fence)].strip()
    return content.strip()


def _fallback_extract(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []

    colon_record = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            colon_record[key.strip()] = value.strip()

    if colon_record:
        return [colon_record]

    try:
        sample = text[:8192]
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        rows = list(reader)
        if rows:
            return rows
    except Exception:
        pass

    return [{"employee_name": lines[0], "notes": text}]
