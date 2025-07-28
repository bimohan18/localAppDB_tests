from pickle import FALSE

import pytest
import requests
import oracledb

# Utility function to connect and check customer existence
def customer_dependencies_removed(custid, db_conn_str):
    """
    Checks if the given customer ID has related records in ACCOUNTS and CUSTOMER_CONTACTS_INFO.
    Returns True if all dependencies are removed, False otherwise.
    """
    query_map = {
        "CUSTOMERS": "SELECT COUNT(*) FROM CUSTOMERS WHERE CUSTID = :1",
        "ACCOUNTS": """
            SELECT COUNT(*) FROM ACCOUNTS WHERE CUST_ACCSLNO IN (
                SELECT CUST_ACCSLNO FROM CUSTOMERS WHERE CUSTID = :1)
        """,
        "CUSTOMER_CONTACTS_INFO": """
            SELECT COUNT(*) FROM CUSTOMER_CONTACTS_INFO WHERE CUST_CONTACTID IN (
                SELECT CUST_CONTACTID FROM CUSTOMERS WHERE CUSTID = :1)
        """
    }
    try:
        with oracledb.connect(db_conn_str) as conn:
            for label, query in query_map.items():
                with conn.cursor() as cursor:
                    cursor.execute(query, [custid])
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"❌ Residual data found in {label} for customer ID {custid} (count: {count})")
                        return False
        return True
    except Exception as e:
        print(f"🛑 DB check failed: {e}")
        return False

@pytest.mark.parametrize("custid, expected_status, case_label, verify_db", [
    # 1. Valid customer ID — expected to delete, return 204
    ("1234500028", 204, "✅ Valid customer ID - Deletion triggers 204", True),
    # 2. Non-existent customer ID — deletion attempt should return 204 or 404 depending on backend behavior
    ("9999", 204, "⚠️ Non-existent customer ID - Still triggers 204 if deletion is idempotent", False),
    # 3. Invalid customer ID (non-integer) — should return 400
    ("12VG", 400, "❌ Non-integer customer ID - Invalid input triggers 400", False),
    # 4. Invalid endpoint path — should return 404
    ("invalid_path", 404, "🚫 Endpoint typo - Route mismatch triggers 404", False)
])

def test_delete_customer_api(base_url, db_conn_str, custid, expected_status, case_label, verify_db):
    if case_label.startswith("🚫"):
        endpoint = f"{base_url}/delCustmr/{custid}"  # typo in endpoint
    else:
        endpoint = f"{base_url}/deleteCustomer/{custid}"

    response = requests.delete(endpoint)

    print(f"\n🔍 Running test: {case_label}")
    assert response.status_code == expected_status
    print(f"🔎 Status Code = {response.status_code} ✅ Matched Expected = {expected_status}")

    # Optional: DB integrity check post-deletion
    if response.status_code == 204 and verify_db:
        still_exists = customer_dependencies_removed(custid, db_conn_str)
        assert not still_exists, f"❌ Customer ID {custid} still exists in DB after supposed deletion!"
        print(f"✅ DB Verification: Customer ID {custid} successfully removed.")