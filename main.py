import yaml
from ingestion.orchestrator import Orchestrator
from storage.storage_manager import StorageManager
from storage.storage_handlers import LocalStorageHandler
from storage.format_handlers import JSONFormatHandler
from storage.enums import StorageType, FormatType
from sources.rest_api_connector import RestAPIConnector

# Load configuration
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Initialize StorageManager
storage_manager = StorageManager()
storage_manager.register_storage_handler(StorageType.LOCAL, LocalStorageHandler())
storage_manager.register_format_handler(FormatType.JSON, JSONFormatHandler())

# Fix case-sensitivity in Enum lookup
storage_type = StorageType[config["storage"]["type"].upper()]
format_type = FormatType[config["storage"]["format"].upper()]

# Initialize connectors
connectors = []
if "rest_api" in config:
    rest_api_config = config["rest_api"]
    rest_connector = RestAPIConnector(
        rest_api_config["base_url"],
        rest_api_config["headers"],
        rest_api_config["endpoints"],
        config["ingestion"]["retry_attempts"],
        config["ingestion"]["retry_delay"]
    )
    connectors.append(rest_connector)

# Start Orchestrator
orchestrator = Orchestrator(connectors=connectors, storage_manager=storage_manager, storage_type=storage_type, format_type=format_type)
orchestrator.start_ingestion()