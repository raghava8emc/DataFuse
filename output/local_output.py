import json
import os
import pandas as pd
from utils.logging_utils import logger

class LocalOutput:
    """Handles saving data to local storage."""
    
    def __init__(self, config):
        self.output_path = config.get("output_path", "data/")

        # Ensure output directory exists
        if not self.test_connection():
            raise RuntimeError(f"Local output directory `{self.output_path}` is not accessible or writable.")
        

    def test_connection(self) -> bool:
        """
        Tests whether the specified output path exists and is writable.
        Ensures ingestion will not fail due to permission issues.
        """
        try:
            # Ensure the directory exists
            os.makedirs(self.output_path, exist_ok=True)

            # Check if we can create a test file
            test_file = os.path.join(self.output_path, ".test_write")
            with open(test_file, "w") as file:
                file.write("test")
            os.remove(test_file)  # Cleanup

            logger.info(f"Successfully validated local output directory: `{self.output_path}`.")
            return True

        except PermissionError:
            logger.error(f"Permission denied: Unable to write to `{self.output_path}`.")
        except OSError as e:
            logger.error(f"OS error when accessing `{self.output_path}`: {e}")
        return False

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

