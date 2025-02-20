import os
import uuid
from sources.rest_api_connector import RestAPIConnector
from sources.sftp_connector import SFTPConnector
from sources.mysql_connector import MySQLConnector
from sources.postgresql_connector import PostgreSQLConnector
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
        
        elif source_type == "mysql":
            return MySQLConnector(
                host=config["host"],
                port=config["port"],
                username=config["username"],
                password=config["password"],
                database=config["database"],
                table_names=config["table_names"],
                temp_dir=self.temp_dir
            )
        
        elif source_type == "mysql":
            return MySQLConnector(
                host=config["host"],
                port=config["port"],
                username=config["username"],
                password=config["password"],
                database=config["database"],
                table_names=config["table_names"],
                temp_dir=self.temp_dir
            )
        
        elif source_type == "postgresql":
            return PostgreSQLConnector(
                host=config["host"],
                port=config["port"],
                username=config["username"],
                password=config["password"],
                database=config["database"],
                table_names=config["table_names"],
                temp_dir=self.temp_dir
            )
        
        return None  
