import os
from multiprocessing import Pool
from utils.timing_utils import log_execution_time
from validation.schema_validator import SchemaValidator
from formatters.json_formatter import JSONFormatter
from formatters.csv_formatter import CSVFormatter
from formatters.xml_formatter import XMLFormatter
from storage.enums import FormatType, StorageType
from output.local_output import LocalOutput

class Orchestrator:
    def __init__(self, connectors, storage_type, format_type, output_config, encoding="utf-8", validation_schemas=None):
        self.connectors = connectors
        self.storage_type = storage_type
        self.format_type = format_type
        self.output_config = output_config
        self.encoding = encoding
        self.validation_schemas = validation_schemas or {}
        self.output_handler = self.get_output_handler()
        self.formatter = self.get_formatter()

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
        else:
            raise ValueError("Unsupported storage type")

    def process_data(self, source, content):
        """Validates, formats, and saves data."""
        schema = self.validation_schemas.get(source, None)
        if schema:
            if self.format_type == FormatType.JSON and not SchemaValidator.validate_json(content, schema):
                return
            if self.format_type == FormatType.CSV and not SchemaValidator.validate_csv(content, schema):
                return
            if self.format_type == FormatType.XML and not SchemaValidator.validate_xml(content, schema):
                return
        
        formatted_data = self.formatter.convert(content, self.encoding)
        self.output_handler.save(formatted_data, f"{source}.{self.format_type.name.lower()}", self.format_type.name)


    @log_execution_time
    def start_ingestion(self):
        """Runs ingestion using multiprocessing."""
        with Pool(processes=os.cpu_count() - 1) as pool:
            ingestion_tasks = [(source, content) for connector in self.connectors for source, content in connector.fetch_data().items()]
            pool.starmap(self.process_data, ingestion_tasks)
