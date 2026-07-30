import urllib.request
import json

# Test 1: Slides API
print("=== Test /api/slides ===")
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/slides')
    d = json.loads(r.read())
    slides = d.get('slides', d if isinstance(d, list) else [])
    print(f"Total slides: {len(slides)}")
    for s in slides[:5]:
        title = s.get('title', 'N/A')[:60]
        sid = s.get('id', 'N/A')
        codes = len(s.get('chunk_codes', []))
        print(f"  {sid}: {title} ({codes} chunks)")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

# Test 2: Homepage
print("\n=== Test / (homepage) ===")
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/')
    html = r.read().decode('utf-8')
    if 'VLearn AI Tutor' in html:
        print(f"PASS - HTML loaded ({len(html)} bytes)")
    else:
        print(f"WARN - HTML loaded but missing expected content")
except Exception as e:
    print(f"FAIL: {e}")

# Test 3: CSS
print("\n=== Test /css/styles.css ===")
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/css/styles.css')
    css = r.read().decode('utf-8')
    print(f"PASS - CSS loaded ({len(css)} bytes)")
except Exception as e:
    print(f"FAIL: {e}")

# Test 4: JS
print("\n=== Test /js/app.js ===")
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/js/app.js')
    js = r.read().decode('utf-8')
    print(f"PASS - JS loaded ({len(js)} bytes)")
except Exception as e:
    print(f"FAIL: {e}")

print("\n=== All basic tests done ===")
