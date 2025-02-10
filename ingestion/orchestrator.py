import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, connectors, storage_manager, storage_type, format_type):
        self.connectors = connectors
        self.storage_manager = storage_manager
        self.storage_type = storage_type
        self.format_type = format_type

    def start_ingestion(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_connector = {executor.submit(connector.fetch_data): connector for connector in self.connectors}
            for future in as_completed(future_to_connector):
                connector = future_to_connector[future]
                try:
                    data = future.result()
                    for source, content in data.items():
                        if content:
                            self.storage_manager.store_data(
                                content, source, self.storage_type, self.format_type
                            )
                    logger.info(f"Successfully processed data from {connector.source_name}")
                except Exception as e:
                    logger.error(f"Error processing data from {connector.source_name}: {e}")