from enum import Enum, auto

class StorageType(Enum):
    LOCAL = auto()
    CLOUD = auto()
    DATABASE = auto()
    QUEUE = auto()

class FormatType(Enum):
    JSON = auto()
    CSV = auto()
    XML = auto()
    PARQUET = auto()