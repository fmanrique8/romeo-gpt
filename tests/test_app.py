import requests

base_url = "http://localhost:8000"  # Replace with the appropriate URL if needed


def test_root():
    response = requests.get(f"{base_url}/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "Vector DB Service"}


def test_create_vector_data():
    vector_data = {"key": "test_key", "value": "test_value"}
    response = requests.post(f"{base_url}/vector/", json=vector_data)
    assert response.status_code == 200
    assert response.json() == {"result": "Vector data created"}


def test_read_vector_data():
    key = "test_key"
    response = requests.get(f"{base_url}/vector/{key}")
    assert response.status_code == 200
    assert response.json() == {"key": key, "value": "test_value"}


def test_update_vector_data():
    key = "test_key"
    updated_vector_data = {"key": key, "value": "updated_test_value"}
    response = requests.put(f"{base_url}/vector/{key}", json=updated_vector_data)
    assert response.status_code == 200
    assert response.json() == {"result": "Vector data updated"}


def test_delete_vector_data():
    key = "test_key"
    response = requests.delete(f"{base_url}/vector/{key}")
    assert response.status_code == 200
    assert response.json() == {"result": "Vector data deleted"}
