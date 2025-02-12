import csv
import io
from formatters.base_formatter import BaseFormatter
from typing import List, Dict, Any, Union

class CSVFormatter(BaseFormatter):
    """Converts structured data to CSV format."""
    
    def convert(self, data: Union[str, bytes, List[Dict[str, Any]]], encoding: str = "utf-8") -> str:
        """Converts structured data to CSV format, handling various CSV structures dynamically."""
        if isinstance(data, bytes):
            data = data.decode(encoding)  # Ensure it's a string


        # Handle CSV string input directly
        if isinstance(data, str):
            lines = data.splitlines()
            reader = csv.reader(lines)
            parsed_data = [row for row in reader]
            
            # Convert parsed data into list of dictionaries if possible
            if parsed_data:
                headers = parsed_data[0]
                data_dicts = [dict(zip(headers, row)) for row in parsed_data[1:]]
                return self._generate_csv(data_dicts, encoding)
            return ""
        
        
        # If data is already in list of dictionaries format, process directly
        if isinstance(data, list) and all(isinstance(row, dict) for row in data):
            return self._generate_csv(data, encoding)
        
        raise ValueError("Unsupported CSV format provided")
    
    def _generate_csv(self, data: List[Dict[str, Any]], encoding: str) -> str:
        """Generates CSV string from list of dictionaries."""
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()