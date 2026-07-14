import os, time, json, datetime
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

REST = f"{SUPABASE_URL}/rest/v1"
STORAGE = f"{SUPABASE_URL}/storage/v1/object"
HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
}

def fetch_pending_jobs():
    params = {
        "status": "eq.pending",
        "job_type": "eq.process_upload",
        "product_id": f"eq.{PRODUCT_ID}",
        "select": "*",
    }
    r = requests.get(f"{REST}/jobs", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def download_file(path):
    r = requests.get(f"{STORAGE}/uploads/{path}", headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.content

def upload_result(path, data):
    url = f"{STORAGE}/results/{path}"
    h = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
         "Content-Type": "application/json", "x-upsert": "true"}
    r = requests.post(url, headers=h, data=data, timeout=60)
    if r.status_code not in (200, 201):
        r = requests.put(url, headers=h, data=data, timeout=60)
    r.raise_for_status()

def insert_records(records):
    if not records:
        return
    r = requests.post(f"{REST}/records", headers=HEADERS, data=json.dumps(records), timeout=60)
    r.raise_for_status()

def update_job(job_id, **fields):
    r = requests.patch(f"{REST}/jobs?id=eq.{job_id}", headers=HEADERS,
                       data=json.dumps(fields), timeout=30)
    r.raise_for_status()

def process(job):
    from processor import extract_certifications
    file_path = job["input_file_path"]
    content = download_file(file_path)
    customer_id = job["customer_id"]
    extracted = extract_certifications(content, file_path, ANTHROPIC_API_KEY)
    records = []
    for item in extracted:
        records.append({
            "product_id": PRODUCT_ID,
            "customer_id": customer_id,
            "title": item["title"],
            "status": item["status"],
            "details": item.get("details", {}),
            "source_file_path": file_path,
            "due_date": item.get("due_date"),
        })
    insert_records(records)
    result_path = f"{PRODUCT_ID}/{job['id']}.json"
    upload_result(result_path, json.dumps({"records": records}))
    return result_path, f"Extracted {len(records)} certifications."

def main():
    print(f"Poller started for product {PRODUCT_ID}. Polling every 10s...")
    while True:
        jobs = fetch_pending_jobs()
        for job in jobs:
            update_job(job["id"], status="processing")
            try:
                result_path, summary = process(job)
                update_job(job["id"], status="completed", output_file_path=result_path, result_summary=summary)
            except Exception as e:
                update_job(job["id"], status="failed", result_summary=str(e))
        time.sleep(10)

if __name__ == "__main__":
    main()
