import xml.etree.ElementTree as ET
from formatters.base_formatter import BaseFormatter

class XMLFormatter(BaseFormatter):
    """Converts structured data to XML format."""
    
    def convert(self, data: dict, encoding: str = "utf-8") -> str:
        root = ET.Element("root")
        self._dict_to_xml(root, data)
        xml_string = ET.tostring(root, encoding=encoding).decode(encoding)
        return xml_string
    
    def _dict_to_xml(self, parent, data):
        for key, value in data.items():
            child = ET.SubElement(parent, key)
            if isinstance(value, dict):
                self._dict_to_xml(child, value)
            else:
                child.text = str(value)