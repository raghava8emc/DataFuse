from storage.storage_manager import StorageManager
from storage.storage_handlers import LocalStorageHandler
from storage.format_handlers import JSONFormatHandler, CSVFormatHandler, ParquetFormatHandler
from storage.enums import StorageType, FormatType

def get_storage_manager():
    """Provides a configured StorageManager instance."""
    storage_manager = StorageManager()
    
    # Register available storage handlers
    storage_manager.register_storage_handler(StorageType.LOCAL, LocalStorageHandler())
    
    # Register available format handlers
    storage_manager.register_format_handler(FormatType.JSON, JSONFormatHandler())
    storage_manager.register_format_handler(FormatType.CSV, CSVFormatHandler())
    storage_manager.register_format_handler(FormatType.PARQUET, ParquetFormatHandler())
    
    return storage_manager