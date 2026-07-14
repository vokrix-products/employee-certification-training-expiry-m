import os, json, re
from openai import OpenAI

def extract_certifications(content, file_path, api_key):
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    text = content.decode("utf-8", errors="replace")
    msg = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"Extract certification records from this file. Return JSON array where each item has: title (MUST be the employee/person name, not the certification type), status (one of: expired, expiring_soon, valid, missing), due_date (ISO date or null), details (dict with certification_type and any other relevant fields). File content:\n{text[:8000]}"}]
    )
    text_out = msg.choices[0].message.content
    m = re.search(r'\[.*\]', text_out, re.DOTALL)
    return json.loads(m.group(0)) if m else []
