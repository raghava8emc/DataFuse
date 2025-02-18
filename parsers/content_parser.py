import json
import csv
import xml.etree.ElementTree as ET
import io
from bs4 import BeautifulSoup
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
            response = response.decode("utf-8")  # Ensure it's a string
        try:
            reader = csv.DictReader(io.StringIO(response))
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
    def parse_html(response: Union[str, bytes]) -> Dict:
        """Parses HTML response, extracting headings, paragraphs, tables, lists, and links."""
        if isinstance(response, bytes):
            response = response.decode("utf-8")
        
        soup = BeautifulSoup(response, "html.parser")

        # Extract Headings (H1, H2, H3, ...)
        headings = {f"h{level}": [h.get_text(strip=True) for h in soup.find_all(f"h{level}")] for level in range(1, 7)}

        # Extract Paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

        # Extract Tables
        tables = []
        for table in soup.find_all("table"):
            table_data = []
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            for row in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if cells:
                    table_data.append(dict(zip(headers, cells)) if headers else cells)
            if table_data:
                tables.append(table_data)

        # Extract Lists (UL, OL)
        lists = {
            "unordered": [[li.get_text(strip=True) for li in ul.find_all("li")] for ul in soup.find_all("ul")],
            "ordered": [[li.get_text(strip=True) for li in ol.find_all("li")] for ol in soup.find_all("ol")]
        }

        # Extract Links
        links = [{"text": a.get_text(strip=True), "url": a["href"]} for a in soup.find_all("a", href=True)]

        return {
            "headings": headings,
            "paragraphs": paragraphs,
            "tables": tables,
            "lists": lists,
            "links": links
        }

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
