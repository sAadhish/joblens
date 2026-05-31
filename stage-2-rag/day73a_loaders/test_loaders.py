# ===================================
# TEST — verify every loader works
# ===================================

from loaders import load_document, clean_text
import os


# -------------------------------------------------------
# Test 1 — Text file loader
# -------------------------------------------------------

print("=" * 55)
print("TEST 1 — Text File Loader")
print("=" * 55)

# sample text file for testing
sample_text = """Sarvam AI Job Description

We are looking for a Backend Engineer.

Requirements:
Strong Python and FastAPI experience.
Knowledge of distributed systems.

About us:
Sarvam AI builds AI for India.
"""

with open("sample_jd.txt", "w") as f:
    f.write(sample_text)

text = load_document("sample_jd.txt")
print(f"Result: {len(text)} characters loaded")
print(f"Preview:\n{text[:200]}")
print()


# -------------------------------------------------------
# Test 2 — PDF loader
# -------------------------------------------------------

print("=" * 55)
print("TEST 2 — PDF Loader")
print("=" * 55)

if os.path.exists("sample.pdf"):
    pdf_text = load_document("sample.pdf")
    print(f"Result: {len(pdf_text)} characters loaded")
    print(f"Preview:\n{pdf_text[:300]}")
else:
    print("No sample.pdf found in this folder.")
    print("Add any PDF file named sample.pdf to test this.")
    print("Tip: use your own resume PDF as sample.pdf")
print()


# -------------------------------------------------------
# Test 3 — Web loader
# -------------------------------------------------------

print("=" * 55)
print("TEST 3 — Web Page Loader")
print("=" * 55)

try:
    web_text = load_document("https://example.com")
    print(f"Result: {len(web_text)} characters loaded")
    print(f"Preview:\n{web_text[:200]}")
except Exception as e:
    print(f"Web loader error: {e}")
print()


# -------------------------------------------------------
# Test 4 — Universal loader auto-detection
# -------------------------------------------------------

print("=" * 55)
print("TEST 4 — Auto Detection")
print("=" * 55)

sources = [
    "sample_jd.txt",
    "https://example.com",
]

for source in sources:
    print(f"Source: {source}")
    try:
        text = load_document(source)
        print(f"  → Loaded {len(text)} characters\n")
    except Exception as e:
        print(f"  → Error: {e}\n")


# -------------------------------------------------------
# Test 5 — Error handling
# -------------------------------------------------------

print("=" * 55)
print("TEST 5 — Error Handling")
print("=" * 55)

bad_sources = [
    "nonexistent_file.pdf",
    "file.xyz",
    "not_a_url",
]

for source in bad_sources:
    try:
        load_document(source)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"  ✓ Correctly caught error for '{source}': {type(e).__name__}")


