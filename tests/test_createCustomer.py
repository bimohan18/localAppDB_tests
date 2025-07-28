import pytest
import requests

# ✅ Smoke Test – Quick Success Path
@pytest.mark.smoke
def test_create_customer_success(base_url, headers, get_valid_payload):
    payload = get_valid_payload()
    res = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert "customer_id" in body
    assert body["message"] == "Customer created successfully"

# ✅ Optional fields can be missing
@pytest.mark.smoke
def test_optional_fields_absence(base_url, headers, get_valid_payload):
    payload = get_valid_payload()
    payload["name"]["middle"] = None
    payload["address"].pop("line2", None)
    payload["address"].pop("line3", None)
    res = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res.status_code == 201

# 🚨 Field-Level Validation Errors
@pytest.mark.fieldcheck
@pytest.mark.parametrize("field_patch,error_msg", [
    (lambda p: p["name"].pop("first"), "name.first"),
    (lambda p: p["name"].pop("last"), "name.last"),
    (lambda p: p.update({"email": "bademail"}), "Email must contain"),
    (lambda p: p.update({"phone": 12345}), "Phone must be"),
    (lambda p: p["document"].update({"type": "SSN", "id": "abc"}), "DOCID for SSN"),
    (lambda p: p.update({"type": "Alien"}), "Customer type must be"),
    (lambda p: p["account"].update({"type": "CURRENT"}), "Account type must be")
])
def test_field_validation_errors(base_url, headers, get_valid_payload, field_patch, error_msg):
    payload = get_valid_payload()
    field_patch(payload)
    res = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res.status_code == 400
    assert error_msg in str(res.json()["details"])

# 🔐 Conflict Cases (409): Duplicate data
@pytest.mark.conflict
def test_duplicate_phone_error(base_url, headers, get_valid_payload):
    payload = get_valid_payload()
    # First creation
    res1 = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res1.status_code == 201
    # Second creation with same phone
    payload["document"]["id"] = "987654321"  # change DOCID to avoid conflict
    res2 = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["error"]

@pytest.mark.conflict
def test_duplicate_docid_error(base_url, headers, get_valid_payload):
    payload = get_valid_payload()
    # First creation
    res1 = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res1.status_code == 201
    # Second creation with same DOCID
    payload["phone"] = 9876543210  # change phone to avoid conflict
    res2 = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res2.status_code == 409
    assert "DOCID" in res2.json()["error"]

# 🚫 Routing Number Check (400)
@pytest.mark.dbcheck
def test_invalid_routing_number(base_url, headers, get_valid_payload):
    payload = get_valid_payload()
    payload["account"]["routing"] = "999999999"  # non-existent routing
    res = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res.status_code == 400
    assert "Invalid routing number" in res.json()["error"]

@pytest.mark.dbcheck
def test_read_customer_after_creation(base_url, headers, get_valid_payload, get_customer_endpoint):
    payload = get_valid_payload()

    # 1️⃣ Create customer
    res_create = requests.post(f"{base_url}/createCustomer", json=payload, headers=headers)
    assert res_create.status_code == 201
    customer_id = res_create.json()["customer_id"]

    # 2️⃣ Read back customer
    read_url = get_customer_endpoint(customer_id)
    res_read = requests.get(read_url, headers=headers)
    assert res_read.status_code == 200

    body = res_read.json()

    # 🔄 Validate key data
    assert body["name"]["first"] == payload["name"]["first"]
    assert body["type"].upper() == payload["type"].upper()
    assert body["document"]["id"] == payload["document"]["id"]
    assert body["email"] == payload["email"]
    assert str(body["phone"]) == str(payload["phone"])

    # 🔗 Validate linkage
    assert "account" in body
    assert body["account"]["routing"] == payload["account"]["routing"]
    assert body["account"]["type"] == payload["account"]["type"]
    assert len(str(body["account"]["number"])) >= 15  # Format check

@pytest.fixture
def cleanup_customer(base_url, headers, delete_customer_endpoint):
    ids = []

    def _register(customer_id):
        ids.append(customer_id)

    yield _register

    # 🔥 Teardown logic
    for cid in ids:
        url = delete_customer_endpoint(cid)
        requests.delete(url, headers=headers)

# Usage
def test_something(dummy, cleanup_customer, customer_id=None):
    cleanup_customer(customer_id)