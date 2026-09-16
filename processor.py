import csv
import io
import re
from datetime import date, datetime

import openpyxl
import pdfplumber

import extraction
from status_engine import compute_statuses


REQUIRED_FIELDS = [
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
]

OPTIONAL_FIELDS = [
    "manager_name",
    "manager_email",
    "hire_date",
    "cert_template_id",
    "verification_status",
    "last_reminder_sent_at",
    "source_document_name",
]

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

FIELD_ALIASES = {
    "employee_name": {"employee_name", "employee name", "employee", "name", "employee full name", "full name", "staff name", "worker name"},
    "employee_email": {"employee_email", "employee email", "email", "email address", "worker email"},
    "employee_phone": {"employee_phone", "employee phone", "phone", "phone number", "mobile", "cell"},
    "employee_id": {"employee_id", "employee id", "employee number", "staff id", "worker id"},
    "job_role": {"job_role", "job role", "role", "job title", "position", "job_title"},
    "work_location": {"work_location", "work location", "location", "site", "work site"},
    "department": {"department", "dept", "business unit", "unit"},
    "certification_type": {"certification_type", "certification type", "certification", "cert type", "license type", "training type", "credential type"},
    "certification_number": {"certification_number", "certification number", "cert number", "certificate number", "license number", "credential number"},
    "issuing_authority": {"issuing_authority", "issuing authority", "authority", "issuer", "issued by", "certification authority", "licensing body"},
    "issue_date": {"issue_date", "issue date", "issued date", "date issued", "certification issue date"},
    "expiration_date": {"expiration_date", "expiration date", "expiry date", "expires", "expiration", "valid until", "valid_until"},
    "renewal_period_months": {"renewal_period_months", "renewal period months", "renewal period", "renewal months", "renewal_months"},
    "required_for_role": {"required_for_role", "required for role", "required", "is required", "role required", "mandatory"},
    "document_file_name_or_link": {"document_file_name_or_link", "document file name or link", "document file name", "document link", "proof document", "document file", "file name", "document_url"},
    "notes": {"notes", "note", "comments", "comment"},
    "manager_name": {"manager_name", "manager name", "manager"},
    "manager_email": {"manager_email", "manager email", "manager email address"},
    "hire_date": {"hire_date", "hire date", "date hired", "start date"},
    "cert_template_id": {"cert_template_id", "cert template id", "template id"},
    "verification_status": {"verification_status", "verification status", "verified", "verification"},
    "last_reminder_sent_at": {"last_reminder_sent_at", "last reminder sent at", "last reminder", "last_reminder"},
    "source_document_name": {"source_document_name", "source document name", "source document", "source file", "source_filename"},
}


_NORMALIZED_ALIASES = {}
for _canonical, _aliases in FIELD_ALIASES.items():
    for _alias in _aliases:
        _normalized_alias = re.sub(r"[^a-z0-9]+", "_", _alias.lower()).strip("_")
        _NORMALIZED_ALIASES[_normalized_alias] = _canonical


def _canonical_key(raw_key):
    if raw_key is None:
        return None
    normalized = re.sub(r"[^a-z0-9]+", "_", str(raw_key).strip().lower()).strip("_")
    return _NORMALIZED_ALIASES.get(normalized)


def _clean(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip()


def _normalize_row(raw_row):
    record = {field: None for field in ALL_FIELDS}
    for raw_key, raw_value in raw_row.items():
        canonical = _canonical_key(raw_key)
        if canonical:
            record[canonical] = _clean(raw_value)
    return record


def _try_pdf(file_bytes):
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        if not text.strip():
            return []
        return extraction.extract_records(text)
    except Exception:
        return []


def _try_excel(file_bytes):
    try:
        workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)

        header = []
        for first_row in rows:
            for idx, value in enumerate(first_row):
                header.append(str(value).strip() if value is not None else f"column_{idx}")
            break

        if not header:
            workbook.close()
            return []

        records = []
        for row in rows:
            if not any(cell is not None for cell in row):
                continue
            record = {}
            for idx, value in enumerate(row):
                if idx < len(header):
                    record[header[idx]] = value
                else:
                    record[f"column_{idx}"] = value
            records.append(record)

        workbook.close()
        return records
    except Exception:
        return []


def _try_text_csv(file_bytes):
    try:
        text = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return []

    if not text.strip():
        return []

    try:
        sample = text[:8192]
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except Exception:
        dialect = csv.excel

    try:
        rows = []
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        for row in reader:
            rows.append(row)

        if rows and any(_canonical_key(key) for key in rows[0].keys()):
            return rows
    except Exception:
        pass

    return extraction.extract_records(text)


def _finalize(raw_rows):
    normalized = [_normalize_row(row) for row in raw_rows if row]
    return compute_statuses(normalized)


def process_file(file_bytes: bytes) -> list[dict]:
    """Process an uploaded file into dashboard-ready employee certification records.

    Format detection order:
    1. PDF via pdfplumber
    2. Excel via openpyxl
    3. UTF-8 CSV/text fallback
    """
    if not file_bytes:
        return []

    rows = _try_pdf(file_bytes)
    if rows:
        return _finalize(rows)

    rows = _try_excel(file_bytes)
    if rows:
        return _finalize(rows)

    rows = _try_text_csv(file_bytes)
    return _finalize(rows)
