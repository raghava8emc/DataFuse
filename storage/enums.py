from enum import Enum, auto

class StorageType(Enum):
    LOCAL = auto()
    MYSQL = auto()

class FormatType(Enum):
    JSON = auto()
    CSV = auto()
    XML = auto()
    PARQUET = auto()