import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from output.local_output import LocalOutput
from storage.enums import StorageType

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, connectors, storage_type, format_type, output_config):
        self.connectors = connectors
        self.storage_type = storage_type
        self.format_type = format_type
        self.output_config = output_config

        if self.storage_type == StorageType.LOCAL:
            self.output_handler = LocalOutput(self.output_config)
        else:
            raise ValueError("Unsupported storage type")

    def start_ingestion(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_connector = {executor.submit(connector.fetch_data): connector for connector in self.connectors}
            for future in as_completed(future_to_connector):
                connector = future_to_connector[future]
                try:
                    data = future.result()
                    for source, content in data.items():
                        if content:
                            self.output_handler.save(content, f"{source}.json")
                    logger.info(f"Successfully processed data from {connector.source_name}")
                except Exception as e:
                    logger.error(f"Error processing data from {connector.source_name}: {e}")