import pytest
import requests
from unittest.mock import patch
from sources.rest_api_connector import RestAPIConnector

@pytest.fixture
def rest_connector():
    """Fixture that creates a RestAPIConnector instance before the test runs"""
    return RestAPIConnector(
        base_url="https://jsonplaceholder.typicode.com",
        headers={"Content-Type": "application/json"},
        endpoints=["posts"],
        retry_attempts=3,
        retry_delay=2
    )

@patch("requests.get")
def test_fetch_data_success(mock_get, rest_connector):
    """Test API connector successfully retrieves data"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"id": 1, "title": "Test"}]
    
    data = rest_connector.fetch_data()
    
    assert "posts" in data
    assert isinstance(data["posts"], list)
    assert len(data["posts"]) > 0

@patch("requests.get")
def test_fetch_data_failure(mock_get, rest_connector):
    """Test API failure scenario (request exception)"""
    mock_get.side_effect = requests.exceptions.RequestException("API error")
    
    data = rest_connector.fetch_data()
    
    assert data["posts"] is None

@patch("requests.get")
def test_fetch_data_retry_logic(mock_get, rest_connector):
    """Test API retry logic in case of multiple failures"""
    mock_get.side_effect = [requests.exceptions.RequestException("API down"),
                            requests.exceptions.RequestException("API down"),
                            mock_get.return_value]
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"id": 1, "title": "Retry Success"}]
    
    data = rest_connector.fetch_data()
    
    assert "posts" in data
    assert isinstance(data["posts"], list)
    assert len(data["posts"]) > 0