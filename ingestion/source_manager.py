import os
import uuid
from sources.rest_api_connector import RestAPIConnector
from sources.sftp_connector import SFTPConnector
from utils.logging_utils import logger

class SourceManager:
    """Manages different data source connectors dynamically."""
    
    def __init__(self):
        self.ingestion_id = str(uuid.uuid4())[:8]  
        self.temp_dir = f"/tmp/ingestion/{self.ingestion_id}"
        os.makedirs(self.temp_dir, exist_ok=True)  

        logger.info(f"Temporary directory for ingestion created: {self.temp_dir}")

    def get_connector(self, source_type: str, config: dict):
        """Returns the appropriate source connector with temp_dir for storage."""
        
        if source_type == "restapi":
            return RestAPIConnector(
                config["base_url"],
                config["headers"],
                config["endpoints"],
                self.temp_dir  
            )

        elif source_type == "sftp":
            print(config)
            return SFTPConnector(
                config["host"],
                config["port"],
                config["username"],
                config["password"],
                config["remote_path"],
                self.temp_dir,
                file_patterns=config["file_patterns"],
                protocol=source_type
            )
        
        return None  
