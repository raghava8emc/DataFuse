import json
from typing import Any
from formatters.base_formatter import BaseFormatter

class JSONFormatter(BaseFormatter):
    """Converts structured data to JSON format."""
    
    def convert(self, data: Any, encoding: str = "utf-8") -> str:
        json_data = json.dumps(data, indent=4)
        return self.encode_data(json_data, encoding)