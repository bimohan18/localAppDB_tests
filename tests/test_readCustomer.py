import json
import pytest
import requests

from tests.utils import assert_customer_structure
#Create three separate invocations of the test function, each time injecting different values
@pytest.mark.parametrize("custid, expected_status, case_label", [
    ("1234500001", 200, "✅ Valid customer - Response 200 aligns"),     # should exist in DB
    ("9999", 404, "⚠️ Non-existent customer - Response 404 aligns"),
    ("12VG", 400, "❌ Invalid customer ID - Response 400 aligns")  # string ID
])
def test_read_customer_api(base_url, custid, expected_status, case_label):
    endpoint = f"{base_url}/readCustomer/{custid}"
    response = requests.get(endpoint)

    print(f"\n🔍 Running test: {case_label}")
    assert response.status_code == expected_status
    print(f"🔎 Status Code = {response.status_code} ✅ Matched Expected = {expected_status}")

