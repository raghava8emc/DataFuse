from jsonschema import validate, ValidationError
import csv
import io
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

class SchemaValidator:
    """Validates data against predefined schemas before storage."""

    @staticmethod
    def validate_json(data: Dict, schema: Dict) -> bool:
        """Validates JSON data against a JSON schema."""
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            print(f"JSON Schema Validation Error: {e.message}")
            return False

    @staticmethod
    def validate_csv(data: List[Dict], schema: List[str]) -> bool:
        """Validates CSV data by ensuring required columns exist."""
        if not data:
            print("CSV Validation Error: Empty data.")
            return False
        
        csv_columns = set(data[0].keys())
        required_columns = set(schema)
        missing_columns = required_columns - csv_columns
        
        if missing_columns:
            print(f"CSV Validation Error: Missing columns {missing_columns}")
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
                print(f"XML Validation Error: Missing tags {missing_tags}")
                return False
            return True
        except ET.ParseError:
            print("XML Validation Error: Invalid XML format.")
            return False