from abc import ABC, abstractmethod
from typing import Any
import codecs

class BaseFormatter(ABC):
    """Abstract base class for data format conversion."""
    
    @abstractmethod
    def convert(self, data: Any, encoding: str = "utf-8") -> str:
        """Converts structured data into the desired format with specified encoding."""
        pass
    
    def encode_data(self, data: str, encoding: str) -> str:
        """Encodes data into the specified encoding format."""
        return codecs.encode(data, encoding, errors='ignore')