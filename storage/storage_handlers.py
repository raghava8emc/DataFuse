from storage.enums import StorageType

class BaseStorageHandler:
    def store(self, data, filename, format_handler):
        raise NotImplementedError

class LocalStorageHandler(BaseStorageHandler):
    def store(self, data, filename, format_handler):
        converted_data = format_handler.convert(data)
        with open(f"data/{filename}.{format_handler.extension}", "w") as file:
            file.write(converted_data)

class CloudStorageHandler(BaseStorageHandler):
    def store(self, data, filename, format_handler):
        pass  # Implement cloud storage logic

class DatabaseStorageHandler(BaseStorageHandler):
    def store(self, data, table_name, format_handler):
        pass  # Implement database storage logic

class MessageQueueHandler(BaseStorageHandler):
    def store(self, data, queue_name, format_handler):
        pass  # Implement message queue logic