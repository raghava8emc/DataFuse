import json
import csv
import xmltodict
import io
from typing import Union, List, Dict
from utils.logging_utils import logger

class ContentParser:
    """Handles different API response content types (JSON, CSV, XML, Binary)."""

    @staticmethod
    def parse_json(response: Union[str, bytes]) -> Union[Dict, List]:
        """Parses JSON response and extracts relevant data keys if wrapped."""
        if isinstance(response, bytes):
            response = response.decode("utf-8") 
        try:
            data = json.loads(response)

            if isinstance(data, dict):
                for key in ["data", "results", "items", "payload", "payloads", "content", "response", "records", "entries", "values", "rows","docs"]:
                    if key in data and isinstance(data[key], list):
                        return data[key]  

            return data if isinstance(data, list) else [data] 
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    @staticmethod
    def parse_csv(response: Union[str, bytes]) -> List[Dict]:
        """Parses CSV response into a list of dictionaries."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  
        try:
            reader = csv.DictReader(io.StringIO(response))
            return [row for row in reader]
        except Exception:
            raise ValueError("Invalid CSV format")

    @staticmethod
    def parse_xml(response: Union[str, bytes]) -> Dict:
        """Parses XML response into a dictionary using `xmltodict`."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  
        try:
            return xmltodict.parse(response, dict_constructor=dict)  
        except Exception as e:
            raise ValueError(f"Invalid XML format: {str(e)}")
    
    @staticmethod
    def parse_html(response: Union[str, bytes]) -> Dict:
        """Parses html response into a dictionary using `xmltodict`."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")  
        try:
            return xmltodict.parse(response, dict_constructor=dict)  
        except Exception as e:
            raise ValueError(f"Invalid HTML format: {str(e)}")

    @staticmethod
    def parse_response(response: Union[str, bytes], content_type: str) -> Union[Dict, List, bytes]:
        """Detects and parses API response based on content type."""
        if "json" in content_type or content_type.endswith("+json"):
            logger.info(f"Parsing JSON format (Detected: {content_type})...")
            return ContentParser.parse_json(response)
        elif "csv" in content_type:
            logger.info("Parsing CSV format...")
            return ContentParser.parse_csv(response)
        elif "xml" in content_type:
            logger.info("Parsing XML format...")
            return ContentParser.parse_xml(response)
        elif "image" in content_type or "octet-stream" in content_type:
            logger.info("Binary content detected (Image/File)... Returning raw bytes.")
            return response  
        elif content_type == "text/html":
            logger.info("Parsing HTML format...")
            return ContentParser.parse_html(response)
        else:
            logger.warning(f"Unsupported content type: {content_type}. Returning raw response.")
            return response  
