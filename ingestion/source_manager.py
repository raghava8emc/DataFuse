import os
import uuid
import time
from sources.rest_api_connector import RestAPIConnector
from sources.sftp_connector import SFTPConnector
from sources.mysql_connector import MySQLConnector
from sources.postgresql_connector import PostgreSQLConnector
from sources.mongodb_connector import MongoDBConnector
from utils.logging_utils import logger

class SourceManager:
    """Manages different data source connectors dynamically."""
    
    def __init__(self):
        """Initialize Source Manager without creating temp directories by default."""
        self.ingestion_id = None
        self.temp_dir = None  # No temp dir initially

    def initialize_temp_dir(self, source_type, storage_type):
        """Create a timestamped temporary directory for ingestion."""
        timestamp = int(time.time())  # Current timestamp
        self.ingestion_id = f"{timestamp}_{source_type}_{storage_type}"  # Unique ID format
        self.temp_dir = f"/tmp/ingestion/{self.ingestion_id}"
        os.makedirs(self.temp_dir, exist_ok=True)  
        logger.info(f"Temporary directory for ingestion created: {self.temp_dir}")

    def get_connector(self, source_type: str, config: dict, storage_type: str, create_temp_dir=False, pool_size=8):
        """Returns the appropriate source connector with temp_dir for storage."""
        
        # Create temp directory only for ingestion (not validation)
        if create_temp_dir and not self.temp_dir:
            self.initialize_temp_dir(source_type, storage_type)

        if source_type == "restapi":
            return RestAPIConnector(
                config["base_url"],
                config["headers"],
                config["endpoints"],
                self.temp_dir if create_temp_dir else None  # Assign temp_dir only for ingestion
            )

        elif source_type == "sftp":
            return SFTPConnector(
                config["host"],
                config["port"],
                config["username"],
                config["password"],
                config["remote_path"],
                self.temp_dir if create_temp_dir else None,
                pool_size=pool_size,
                file_patterns=config.get("file_patterns", []),
                protocol=source_type
            )
        
        elif source_type == "mysql":
            return MySQLConnector(
                host=config["host"],
                port=config["port"],
                username=config["username"],
                password=config["password"],
                database=config["database"],
                table_names=config["table_names"],
                temp_dir=self.temp_dir if create_temp_dir else None,
                pool_size=pool_size  
            )
        
        elif source_type == "postgresql":
            return PostgreSQLConnector(
                host=config["host"],
                port=config["port"],
                username=config["username"],
                password=config["password"],
                database=config["database"],
                table_names=config["table_names"],
                temp_dir=self.temp_dir if create_temp_dir else None,
                pool_size=pool_size  
            )
        
        elif source_type == "mongodb":
            return MongoDBConnector(
                host=config["host"],
                port=config["port"],
                username=config["username"],
                password=config["password"],
                database=config["database"],
                collection_names=config["collection_names"],
                temp_dir=self.temp_dir if create_temp_dir else None,
                pool_size=pool_size    # Assign temp_dir only for ingestion
            )
        
        return None  
