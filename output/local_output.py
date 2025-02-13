import json
import os
import pandas as pd

class LocalOutput:
    """Handles saving data to local storage."""
    
    def __init__(self, config):
        self.output_path = config.get("output_path", "data/")

        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)

    def save(self, data, filename, format_type="json"):
        """Saves structured data based on format type."""
        file_path = os.path.join(self.output_path, filename)

        if format_type.lower() == "json":
            self._save_json(data, file_path)
        elif format_type.lower() == "csv":
            self._save_csv(data, file_path)
        else:
            raise ValueError(f"Unsupported file format: {format_type}")

    def _save_json(self, data, file_path):
        """Saves data as JSON."""
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        
        if not isinstance(data, (dict, list, str)):
            raise TypeError("Data must be JSON serializable (dict, list, or str)")
        
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def _save_csv(self, data, file_path):

        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise TypeError("CSV data must be a list of dictionaries")

        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, encoding="utf-8") 

