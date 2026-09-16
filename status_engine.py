import calendar
from datetime import date, datetime
from collections import defaultdict


STATUS_MISSING_REQUIRED = "missing_required_certification:critical"
STATUS_EXPIRED = "expired:critical"
STATUS_EXPIRING_0_30 = "expiring_0_30_days:critical"
STATUS_EXPIRING_31_60 = "expiring_31_60_days:warning"
STATUS_EXPIRING_61_90 = "expiring_61_90_days:warning"
STATUS_VALID = "valid:good"
STATUS_FLAGGED = "flagged_for_review:warning"
STATUS_UNVERIFIED = "unverified_or_document_missing:warning"
STATUS_DUPLICATE = "duplicate_or_conflicting_record:warning"
STATUS_NO_EXPIRATION = "no_expiration_date:warning"


def _parse_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"true", "yes", "y", "1", "required", "mandatory", "required_for_role"}:
        return True
    if s in {"false", "no", "n", "0", "not required", "optional", "none", "null", ""}:
        return False
    return None


def _has_value(value):
    return value is not None and str(value).strip() != ""


def _parse_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    raw = str(value).strip()
    if not raw or raw.lower() in {"none", "null", "na", "n/a"}:
        return None

    try:
        return datetime.fromisoformat(raw).date()
    except Exception:
        pass

    for fmt in (
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%b %d %Y",
        "%d %b %Y",
    ):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    return None


def _parse_int(value):
    try:
        return int(float(str(value).strip()))
    except Exception:
        return None


def _add_months(start_date, months):
    month_index = start_date.month - 1 + int(months)
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _duplicate_key(record):
    employee = str(record.get("employee_name") or "").strip().lower()
    certification = str(record.get("certification_type") or "").strip().lower()
    issuer = str(record.get("issuing_authority") or "").strip().lower()

    if not employee or not certification or not issuer:
        return None

    return employee, certification, issuer


def _make_title(record):
    employee = str(record.get("employee_name") or "").strip()
    return employee or "Unknown Employee"


def _make_details(record):
    details = {}
    for key, value in record.items():
        if key in {"employee_name", "title", "status", "due_date"}:
            continue
        details[key] = value
    return details


def _compute_due_date(record, today):
    expiration = _parse_date(record.get("expiration_date"))
    if expiration:
        return expiration.isoformat()

    issue_date = _parse_date(record.get("issue_date"))
    renewal_months = _parse_int(record.get("renewal_period_months"))
    if issue_date and renewal_months:
        return _add_months(issue_date, renewal_months).isoformat()

    return None


def _compute_status(record, today, duplicate_flag):
    required = _parse_bool(record.get("required_for_role")) is True
    cert_type = str(record.get("certification_type") or "").strip()
    cert_number = str(record.get("certification_number") or "").strip()
    issuer = str(record.get("issuing_authority") or "").strip()
    doc = str(record.get("document_file_name_or_link") or "").strip()

    expiration_raw = record.get("expiration_date")
    issue_raw = record.get("issue_date")
    expiration = _parse_date(expiration_raw)
    issue = _parse_date(issue_raw)

    if required and not cert_type:
        return STATUS_MISSING_REQUIRED

    if not cert_type:
        if not _has_value(expiration_raw):
            return STATUS_NO_EXPIRATION
        return STATUS_FLAGGED

    if cert_type and not cert_number:
        return STATUS_FLAGGED

    if cert_type and not issuer:
        return STATUS_FLAGGED

    if not _has_value(expiration_raw):
        return STATUS_NO_EXPIRATION

    if expiration is None:
        return STATUS_FLAGGED

    if _has_value(issue_raw) and issue is None:
        return STATUS_FLAGGED

    days = (expiration - today).days

    if days < 0:
        return STATUS_EXPIRED

    if days <= 30:
        return STATUS_EXPIRING_0_30

    if days <= 60:
        return STATUS_EXPIRING_31_60

    if days <= 90:
        return STATUS_EXPIRING_61_90

    if not doc:
        return STATUS_UNVERIFIED

    if duplicate_flag:
        return STATUS_DUPLICATE

    return STATUS_VALID


def compute_statuses(records, today=None):
    if today is None:
        today = date.today()

    if not records:
        return []

    duplicate_counts = defaultdict(int)
    for record in records:
        key = _duplicate_key(record)
        if key is not None:
            duplicate_counts[key] += 1

    result = []
    for record in records:
        record = dict(record)
        duplicate_key = _duplicate_key(record)
        duplicate_flag = duplicate_key is not None and duplicate_counts[duplicate_key] > 1

        status = _compute_status(record, today, duplicate_flag)
        due_date = _compute_due_date(record, today)
        title = _make_title(record)
        details = _make_details(record)

        result.append(
            {
                "title": title,
                "status": status,
                "details": details,
                "due_date": due_date,
            }
        )

    return result
