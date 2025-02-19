from jsonschema import validate, ValidationError
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Union
from utils.logging_utils import logger

class SchemaValidator:
    """Validates data against predefined schemas before storage."""

    @staticmethod
    def validate(data: Union[Dict, List, str], schema: Union[Dict, List], format_type) -> bool:
        """Generic method to validate data against a schema based on format type."""
        if format_type == "JSON":
            return SchemaValidator.validate_json(data, schema)
        elif format_type == "CSV":
            return SchemaValidator.validate_csv(data, schema)
        elif format_type == "XML":
            return SchemaValidator.validate_xml(data, schema)
        else:
            logger.error(f"Unsupported format `{format_type}` for validation.")
            return False

    @staticmethod
    def validate_json(data: Dict, schema: Dict) -> bool:
        """Validates JSON data against a JSON schema."""
        if not schema:
            logger.warning("Skipping JSON validation (no schema provided).")
            return True  # If no schema is given, assume it's valid
        
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            logger.error(f"JSON Schema Validation Error: {e.message}")
            return False

    @staticmethod
    def validate_csv(data: List[Dict], schema: List[str]) -> bool:
        """Validates CSV data by ensuring required columns exist."""
        if not data:
            logger.error("CSV Validation Error: Empty data.")
            return False

        csv_columns = set(data[0].keys())
        required_columns = set(schema)
        missing_columns = required_columns - csv_columns

        if missing_columns:
            logger.error(f"CSV Validation Error: Missing columns {missing_columns}")
            return False
        return True

    @staticmethod
    def validate_xml(data: str, schema_tags: List[str]) -> bool:
        """Validates XML data by ensuring required tags exist."""
        try:
            root = ET.fromstring(data)
            present_tags = {child.tag for child in root}
            missing_tags = set(schema_tags) - present_tags

            if missing_tags:
                logger.error(f"XML Validation Error: Missing tags {missing_tags}")
                return False
            return True
        except ET.ParseError:
            logger.error("XML Validation Error: Invalid XML format.")
            return False
