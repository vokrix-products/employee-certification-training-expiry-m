import os, json, anthropic

def extract_certifications(content, file_path, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        text = content.decode("utf-8", errors="replace")
    else:
        text = content.decode("utf-8", errors="replace")
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"Extract certification records from this file. Return JSON array where each item has: title (str), status (one of: expired, expiring_soon, valid, missing), due_date (ISO date or null), details (dict). File content:\n{text[:8000]}"}]
    )
    import re
    text_out = msg.content[0].text
    m = re.search(r'\[.*\]', text_out, re.DOTALL)
    return json.loads(m.group(0)) if m else []
