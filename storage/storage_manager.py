from storage.enums import StorageType, FormatType

class StorageManager:
    def __init__(self):
        self.storage_handlers = {}
        self.format_handlers = {}

    def register_storage_handler(self, storage_type: StorageType, handler):
        self.storage_handlers[storage_type] = handler

    def register_format_handler(self, format_type: FormatType, handler):
        self.format_handlers[format_type] = handler

    def store_data(self, data, filename, storage_type: StorageType, format_type: FormatType):
        storage_handler = self.storage_handlers.get(storage_type)
        format_handler = self.format_handlers.get(format_type)
        if not storage_handler or not format_handler:
            raise ValueError("Invalid storage or format type")
        storage_handler.store(data, filename, format_handler)