#Create a reusable test client for your Flask app
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"

@pytest.fixture
def get_customer_endpoint(base_url):
    def wrapper(custid):
        return f"{base_url}/readCustomer/{custid}"
    return wrapper

@pytest.fixture
def headers():
    return {
        "Content-Type": "application/json"
    }