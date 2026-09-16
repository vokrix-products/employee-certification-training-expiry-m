from processor import process_file
from status_engine import compute_statuses


def test_missing_required_certification():
    records = [
        {
            "employee_name": "Noah Williams",
            "required_for_role": "true",
            "certification_type": "",
            "certification_number": "",
            "issuing_authority": "",
            "expiration_date": "",
            "document_file_name_or_link": "",
        }
    ]

    result = compute_statuses(records)
    assert result[0]["status"] == "missing_required_certification:critical"
    assert result[0]["title"] == "Noah Williams"
    assert result[0]["due_date"] is None


def test_valid_certification_from_csv_bytes():
    csv_bytes = (
        b"employee_name,employee_email,certification_type,certification_number,issuing_authority,"
        b"issue_date,expiration_date,required_for_role,document_file_name_or_link\n"
        b"Bob,bob@example.com,CPR,CPR-100,Red Cross,2025-01-01,2099-01-01,true,bob_cpr.pdf\n"
    )

    result = process_file(csv_bytes)
    assert result[0]["title"] == "Bob"
    assert result[0]["status"] == "valid:good"
    assert result[0]["due_date"] == "2099-01-01"
    assert isinstance(result[0]["details"], dict)


def test_no_expiration_date():
    records = [
        {
            "employee_name": "Priya Shah",
            "certification_type": "Background Check",
            "certification_number": "BG-1",
            "issuing_authority": "State Licensing",
            "expiration_date": "",
            "required_for_role": "true",
            "document_file_name_or_link": "priya.pdf",
        }
    ]

    result = compute_statuses(records)
    assert result[0]["status"] == "no_expiration_date:warning"
    assert result[0]["title"] == "Priya Shah"
    assert result[0]["due_date"] is None


def test_expired_certification():
    records = [
        {
            "employee_name": "Dana Ortiz",
            "certification_type": "First Aid/CPR",
            "certification_number": "CPR-9",
            "issuing_authority": "Red Cross",
            "issue_date": "2020-01-01",
            "expiration_date": "2020-06-01",
            "required_for_role": "true",
            "document_file_name_or_link": "dana.pdf",
        }
    ]

    result = compute_statuses(records)
    assert result[0]["status"] == "expired:critical"
    assert result[0]["due_date"] == "2020-06-01"


def test_duplicate_detection():
    record = {
        "employee_name": "Sam Reed",
        "certification_type": "Forklift",
        "certification_number": "FL-1",
        "issuing_authority": "Safety Co",
        "issue_date": "2024-01-01",
        "expiration_date": "2099-01-01",
        "required_for_role": "true",
        "document_file_name_or_link": "sam.pdf",
    }

    result = compute_statuses([dict(record), dict(record)])
    assert result[0]["status"] == "duplicate_or_conflicting_record:warning"
    assert result[1]["status"] == "duplicate_or_conflicting_record:warning"


def main():
    tests = [
        test_missing_required_certification,
        test_valid_certification_from_csv_bytes,
        test_no_expiration_date,
        test_expired_certification,
        test_duplicate_detection,
    ]

    passed = 0
    for test in tests:
        test()
        passed += 1
        print("PASS: " + test.__name__)

    print(str(passed) + " tests passed")


if __name__ == "__main__":
    main()
