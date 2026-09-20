# tests/test_resources.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.resources import (
    get_companies_resource,
    get_resume_resource,
    get_jd_resource
)

print("=" * 55)
print("TEST 1 — Companies Resource")
print("=" * 55)
print(get_companies_resource())

print()
print("=" * 55)
print("TEST 2 — Resume Resource")
print("=" * 55)
print(get_resume_resource()[:400])

print()
print("=" * 55)
print("TEST 3 — JD Resource (Sarvam AI)")
print("=" * 55)
print(get_jd_resource("Sarvam AI"))

print()
print("=" * 55)
print("TEST 4 — JD Resource (nonexistent company)")
print("=" * 55)
print(get_jd_resource("Google"))