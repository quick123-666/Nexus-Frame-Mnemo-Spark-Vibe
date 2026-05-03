import requests
import sys

try:
    r = requests.post('http://localhost:8000/api/task', json={'task': 'Test', 'context_tags': ['test']})
    print(f'Status: {r.status_code}')
    print(f'Content-Type: {r.headers.get("Content-Type")}')
    print(f'Response: {r.text[:1000]}')
except Exception as e:
    print(f'Request failed: {e}')
