import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Test AI: suggest questions
print("=== Test /api/suggest-questions ===")
try:
    data = json.dumps({"level": "coban"}).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/suggest-questions',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    r = urllib.request.urlopen(req, timeout=30)
    result = json.loads(r.read().decode('utf-8'))
    questions = result.get('questions', [])
    print(f"Got {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print(f"Level info: {result.get('level_info', {})}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print("\nDone!")
