from abc import ABC, abstractmethod
from storage.enums import StorageType

class BaseOutput(ABC):
    def __init__(self, storage_type: StorageType, config: dict):
        self.storage_type = storage_type
        self.config = config

    @abstractmethod
    def save(self, data, filename):
        """Method to be implemented for each storage type."""
        pass