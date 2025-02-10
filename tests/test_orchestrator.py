import pytest
from unittest.mock import MagicMock
from ingestion.orchestrator import Orchestrator
from storage.storage_manager import StorageManager
from storage.enums import StorageType, FormatType

@pytest.fixture
def mock_connectors():
    """Creates a mock data connector that returns fake data"""
    connector = MagicMock()
    connector.source_name = "MockSource"
    connector.fetch_data.return_value = {"mock_data": [{"id": 1, "name": "Test"}]}
    return [connector]

@pytest.fixture
def mock_storage_manager():
    """Creates a mock storage manager that tracks store_data calls"""
    return MagicMock(spec=StorageManager)

def test_orchestrator_ingestion(mock_connectors, mock_storage_manager):
    """Test orchestrator ingestion process"""
    orchestrator = Orchestrator(
        connectors=mock_connectors,
        storage_manager=mock_storage_manager,
        storage_type=StorageType.LOCAL,
        format_type=FormatType.JSON
    )
    orchestrator.start_ingestion()
    
    # Ensure store_data was called for the mock source
    assert mock_storage_manager.store_data.call_count == 1
    mock_storage_manager.store_data.assert_called_with(
        [{"id": 1, "name": "Test"}], "mock_data", StorageType.LOCAL, FormatType.JSON
    )