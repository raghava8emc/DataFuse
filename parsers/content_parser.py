import json
import csv
import xml.etree.ElementTree as ET
from typing import Union, List, Dict
from utils.logging_utils import logger

class ContentParser:
    """Handles different API response content types (JSON, CSV, XML)."""

    @staticmethod
    def parse_json(response: Union[str, bytes]) -> Union[Dict, List]:
        """Parses JSON response into a dictionary or list."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  # Ensure it's a string
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    @staticmethod
    def parse_csv(response: Union[str, bytes]) -> List[Dict]:
        """Parses CSV response into a list of dictionaries."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  # Ensure it's a string
        try:
            lines = response.splitlines()
            reader = csv.DictReader(lines)
            return [row for row in reader]
        except Exception:
            raise ValueError("Invalid CSV format")

    @staticmethod
    def parse_xml(response: Union[str, bytes]) -> Dict:
        """Parses XML response into a dictionary."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  # Ensure it's a string
        try:
            root = ET.fromstring(response)
            return ContentParser._xml_to_dict(root)
        except ET.ParseError:
            raise ValueError("Invalid XML format")
    
    @staticmethod
    def _xml_to_dict(element) -> Dict:
        """Recursively converts an XML element into a dictionary."""
        return {element.tag: {child.tag: ContentParser._xml_to_dict(child) if len(child) else child.text for child in element}}

    @staticmethod
    def parse_response(response: Union[str, bytes], content_type: str) -> Union[Dict, List]:
        """Detects and parses API response based on content type."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  # Decode bytes before processing
        
        if content_type == "application/json":
            logger.info("Parsing JSON format...")
            return ContentParser.parse_json(response)
        elif content_type in ("text/csv", "application/csv"):
            logger.info("Parsing CSV format... ")
            return ContentParser.parse_csv(response)
        elif content_type in ("application/xml", "text/xml"):
            logger.info("Parsing XML format... ")
            return ContentParser.parse_xml(response)
        else:
            logger.error(f"Unsupported content type: {content_type}")
            raise ValueError(f"Unsupported content type: {content_type}")
