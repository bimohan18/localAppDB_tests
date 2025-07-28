import json
import pytest
import requests

from tests.utils import assert_customer_structure

@pytest.mark.parametrize("custid, expected_status, case_label", [
    # 1. Valid customer ID — should return 200
    ("1234500001", 200, "✅ Valid customer - Response 200 aligns"),
    # 2. Non-existent customer ID — should return 404
    ("9999", 404, "⚠️ Non-existent customer - Response 404 aligns"),
    # 3. Invalid customer ID (non-integer) — should return 400 or 404 depending on backend behavior
    ("12VG", 400, "❌ Invalid customer ID - Response 400 aligns"),
    # 4. Invalid endpoint URL — should return 404
    ("invalid_path", 404, "🚫 Invalid endpoint - Route mismatch triggers 404")
])
def test_read_customer_api(base_url, custid, expected_status, case_label):
    if custid == "invalid_path":
        endpoint = f"{base_url}/redCustmr/{custid}"  # simulate typo in endpoint
    else:
        endpoint = f"{base_url}/readCustomer/{custid}"

    response = requests.get(endpoint)

    print(f"\n🔍 Running test: {case_label}")
    assert response.status_code == expected_status
    print(f"🔎 Status Code = {response.status_code} ✅ Matched Expected = {expected_status}")

    # Optional: If status is 200, validate response structure
    if response.status_code == 200:
        data = response.json()
        assert_customer_structure(data)  # Custom utility that verifies expected keys and layout