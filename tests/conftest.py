#Create a reusable test client for your Flask app
import pytest
import requests

@pytest.fixture(scope="session")
def db_conn_str():
    return "MASTERDBA/password@localhost:1521/xe"

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"

@pytest.fixture
def get_customer_endpoint(base_url):
    def wrapper(custid):
        return f"{base_url}/readCustomer/{custid}"
    return wrapper

@pytest.fixture
def delete_customer_endpoint(base_url):
    def wrapper(custid):
        return f"{base_url}/deleteCustomer/{custid}"
    return wrapper

@pytest.fixture
def headers():
    return {
        "Content-Type": "application/json"
    }

@pytest.fixture
def get_valid_payload():
    def _payload():
        return {
            "name": {
                "first": "DB",
                "middle": "",
                "last": "User1030"
            },
            "type": "Personal",
            "document": {
                "id": "123456789",
                "type": "SSN"
            },
            "address": {
                "line1": "101 First Street",
                "line2": "Suite 500",
                "line3": "",
                "city": "East Providence",
                "zip": "02914",
                "state": "RI",
                "country": "USA"
            },
            "email": "indira@co.io",
            "phone": 1234567890,
            "account": {
                "type": "CHECKING",
                "routing": "ABC0005001"
            }
        }
    return _payload