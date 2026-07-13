"""Extract certification records from uploaded files (PDF or CSV) using Claude API."""

import csv
import io
import json
import os
import tempfile
from typing import Any, Dict, List

import anthropic


def extract_certifications(
    content: bytes, file_path: str, api_key: str
) -> List[Dict[str, Any]]:
    """Parse uploaded file and return list of certification records."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".csv", ".txt"):
        return _extract_csv(content)
    elif ext in (".pdf",):
        return _extract_pdf(content, api_key)
    else:
        # Unsupported file type – return empty
        return []


def _extract_csv(content: bytes) -> List[Dict[str, Any]]:
    """Parse CSV content with expected headers: name, certification, issue_date, expiry_date."""
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    records: List[Dict[str, Any]] = []
    for row in reader:
        title = row.get("certification") or row.get("title") or "Unknown"
        issue_date = row.get("issue_date") or row.get("issued_date") or ""
        expiry_date = row.get("expiry_date") or row.get("expiration_date") or ""
        employee = row.get("name") or row.get("employee") or "Unknown"

        status = _compute_status(expiry_date)

        records.append(
            {
                "title": f"{employee} - {title}",
                "status": status,
                "details": {
                    "employee": employee,
                    "certification": title,
                    "issue_date": issue_date,
                    "expiry_date": expiry_date,
                },
                "due_date": expiry_date if expiry_date else None,
            }
        )
    return records


def _extract_pdf(content: bytes, api_key: str) -> List[Dict[str, Any]]:
    """Use Claude to extract certification data from PDF text."""
    # Extract text using PyMuPDF
    try:
        import fitz

        doc = fitz.open(stream=content, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
    except Exception:
        full_text = content.decode("utf-8", errors="replace")

    if not full_text.strip():
        return []

    prompt = f"""Extract employee certification/license/training records from the following text.

Return a JSON array of objects with these fields:
- "employee": string
- "certification": string
- "issue_date": string or null
- "expiry_date": string or null

Text:
{full_text}"""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.content[0].text.strip()
    # Try to parse JSON array from answer
    if answer.startswith("```json"):
        answer = answer[7:]
    if answer.startswith("```"):
        answer = answer[3:]
    if answer.endswith("```"):
        answer = answer[:-3]
    answer = answer.strip()

    try:
        extracted = json.loads(answer)
    except json.JSONDecodeError:
        return []

    records = []
    for item in extracted:
        employee = item.get("employee", "Unknown")
        cert = item.get("certification", "Unknown")
        title = f"{employee} - {cert}"
        expiry_date = item.get("expiry_date") or ""
        status = _compute_status(expiry_date)
        records.append(
            {
                "title": title,
                "status": status,
                "details": {
                    "employee": employee,
                    "certification": cert,
                    "issue_date": item.get("issue_date"),
                    "expiry_date": expiry_date,
                },
                "due_date": expiry_date if expiry_date else None,
            }
        )
    return records


def _compute_status(expiry_date: str) -> str:
    """Determine status based on expiry date: valid, expiring_soon, expired, or missing."""
    if not expiry_date:
        return "missing"
    from datetime import datetime

    try:
        dt = datetime.strptime(expiry_date, "%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(expiry_date, "%m/%d/%Y")
        except ValueError:
            return "missing"

    from datetime import date, timedelta

    today = date.today()
    if dt.date() < today:
        return "expired"
    elif dt.date() <= today + timedelta(days=30):
        return "expiring_soon"
    else:
        return "valid"
