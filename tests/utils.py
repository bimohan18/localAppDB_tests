#Helper for extracting nested fields from JSON responses or validating structures
def assert_customer_structure(data):
    assert "customer" in data
    assert "contact" in data
    assert "account" in data

    customer = data["customer"]
    assert "id" in customer
    assert "first_name" in customer
    assert "last_name" in customer

    # Contact section checks
    contact = data["contact"]
    assert "email" in contact
    assert "phone" in contact

    # Account section checks
    account = data["account"]
    assert "number" in account
    assert "routing" in account
    # Add more assertions as needed
