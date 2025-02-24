import os
import shutil
import json
import concurrent.futures
from utils.timing_utils import log_execution_time
from validation.schema_validator import SchemaValidator
from formatters.json_formatter import JSONFormatter
from formatters.csv_formatter import CSVFormatter
from formatters.xml_formatter import XMLFormatter
from storage.enums import FormatType, StorageType
from output.local_output import LocalOutput
from output.mysql_output import MySQLOutput
from output.postgres_output import PostgreSQLOutput
from output.mongodb_output import MongoDBOutput
from utils.logging_utils import logger
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

class Orchestrator:
    def __init__(self, connectors, storage_type, format_type, output_config, temp_dir, pool_size=8, encoding="utf-8", validation_schemas=None):
        self.connectors = connectors
        self.storage_type = storage_type
        self.format_type = format_type
        self.output_config = output_config
        self.encoding = encoding
        self.validation_schemas = validation_schemas or {}
        self.temp_dir = temp_dir
        self.downloaded_files = []
        self.output_handler = self.get_output_handler()
        self.formatter = self.get_formatter()
        self.max_connections = min(pool_size, os.cpu_count())

        if not self.validate_input_sources():
            logger.error("Input source validation failed. Stopping ingestion.")
            raise RuntimeError("Input source validation failed.")

        if not self.validate_output_source():
            logger.error("Output storage validation failed. Stopping ingestion.")
            raise RuntimeError("Output storage validation failed.")

    def validate_input_sources(self) -> bool:
        """
        Validates all input sources before starting ingestion.
        Ensures connection validity for REST API, SFTP, MySQL, PostgreSQL, and MongoDB.
        """
        logger.info("Validating input sources...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_source = {executor.submit(connector.test_connection): connector for connector in self.connectors}

            for future in concurrent.futures.as_completed(future_to_source):
                connector = future_to_source[future]
                try:
                    if not future.result():
                        logger.error(f"Input validation failed for `{connector}`.")
                        return False  # Stop if any source fails
                except Exception as e:
                    logger.error(f"Exception during input validation for `{connector}`: {e}")
                    return False

        logger.info("All input sources validated successfully.")
        return True

    def validate_output_source(self) -> bool:
        """
        Validates the output storage before ingestion starts.
        Ensures connection validity for MySQL, PostgreSQL, MongoDB, and Local storage.
        """
        logger.info("Validating output storage...")

        try:
            if not self.output_handler.test_connection():
                logger.error(f"Output validation failed for `{self.storage_type.name}`.")
                return False
        except Exception as e:
            logger.error(f"Exception during output validation for `{self.storage_type.name}`: {e}")
            return False

        logger.info(f"Output storage `{self.storage_type.name}` validated successfully.")
        return True

    def get_formatter(self):
        if self.format_type == FormatType.JSON:
            return JSONFormatter()
        elif self.format_type == FormatType.CSV:
            return CSVFormatter()
        elif self.format_type == FormatType.XML:
            return XMLFormatter()
        else:
            raise ValueError("Unsupported format type")
    
    def get_output_handler(self):
        if self.storage_type == StorageType.LOCAL:
            return LocalOutput(self.output_config)
        elif self.storage_type == StorageType.MYSQL:
            return MySQLOutput(self.output_config)
        elif self.storage_type == StorageType.POSTGRESQL:
            return PostgreSQLOutput(self.output_config)
        elif self.storage_type == StorageType.MONGODB:
            return MongoDBOutput(self.output_config)
        else:
            raise ValueError("Unsupported storage type")



    def process_data(self, file_path, source, endpoint):
        """Reads, validates, formats, and saves data from the file."""
        file_path = Path(file_path)
        input_format = file_path.suffix.lstrip(".").lower()
        output_format = self.format_type.name.lower()
        
        try:
            # If storage type is LOCAL, define an output directory
            output_dir = Path(self.output_handler.output_path) if self.storage_type == StorageType.LOCAL else None
            
            # Case 1: If file is already in required format, move it directly (LOCAL only)
            if self.storage_type == StorageType.LOCAL and input_format == output_format:
                output_file_path = output_dir / file_path.name
                shutil.move(file_path, output_file_path)
                logger.info(f"Moved `{file_path.name}` to `{output_file_path}` without processing (already in `{output_format}`).")
                return

            # Read file content based on format
            content = None
            if input_format == "json":
                with file_path.open("r", encoding="utf-8") as file:
                    content = json.load(file)  
            elif input_format == "csv":
                with file_path.open("r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    content = [row for row in reader]  
            elif input_format == "xml":
                with file_path.open("r", encoding="utf-8") as file:
                    content = ET.parse(file).getroot()
                    content = self._xml_to_dict(content)  
            else:
                logger.error(f"Unsupported input format `{input_format}` for `{file_path.name}`.")
                return

            # Validate against schema
            schema = self.validation_schemas.get(source)
            if schema and not SchemaValidator.validate(content, schema, self.format_type):
                logger.error(f"Schema validation failed for `{file_path.name}`.")
                return

            # Case 2: Save processed data
            logger.info(f"Saving processed data for `{file_path.name}`...")

            if self.storage_type == StorageType.MYSQL:
                MySQLOutput(self.output_config).save(content, source, endpoint)
            elif self.storage_type == StorageType.POSTGRESQL:
                PostgreSQLOutput(self.output_config).save(content, source, endpoint)
            elif self.storage_type == StorageType.MONGODB:
                MongoDBOutput(self.output_config).save(content, source, endpoint)
            else:  
                output_filename = file_path.stem + f".{output_format}"
                output_file_path = output_dir / output_filename
                self.output_handler.save(content, output_filename, output_format)
                logger.info(f"Successfully processed `{file_path.name}` into `{output_file_path}`")

            logger.info(f"Successfully processed `{file_path.name}`")

        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON file `{file_path.name}` (invalid format).")
        except Exception as e:
            logger.error(f"Error processing file `{file_path.name}`: {e}")



    @log_execution_time
    def start_ingestion(self):
        """Runs ingestion using multithreading (I/O-bound)."""
        logger.info(f"Starting ingestion process...")

        for connector in self.connectors:
            for source, file_path in connector.fetch_data().items():
                if file_path:  
                    self.downloaded_files.append((file_path, source, source))

            logger.info(f"Complete Data written to temporary directory `{connector.temp_dir}` successfully.")

        

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_task = {
                executor.submit(self.process_data, file_path, source, source): source
                for file_path, source, source in self.downloaded_files
            }

            for future in concurrent.futures.as_completed(future_to_task):
                source = future_to_task[future]
                try:
                    future.result()
                    logger.info(f"Finished processing `{source}` successfully.")
                except Exception as e:
                    logger.error(f"Error processing `{source}`: {e}")

        logger.info("Ingestion process completed!")

        shutil.rmtree(self.temp_dir)
        logger.info(f"Temporary directory {self.temp_dir} deleted.")