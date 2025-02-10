import json
from storage.enums import FormatType

class BaseFormatHandler:
    def convert(self, data):
        raise NotImplementedError

class JSONFormatHandler(BaseFormatHandler):
    extension = "json"
    def convert(self, data):
        return json.dumps(data, indent=4)

class CSVFormatHandler(BaseFormatHandler):
    extension = "csv"
    def convert(self, data):
        pass  # Implement CSV conversion

class ParquetFormatHandler(BaseFormatHandler):
    extension = "parquet"
    def convert(self, data):
        pass  # Implement Parquet conversion