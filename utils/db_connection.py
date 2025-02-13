from abc import ABC, abstractmethod
from typing import Dict
import mysql.connector
from mysql.connector import pooling

class BaseDBConnection(ABC):
    """Abstract base class for database connections."""

    _connection_pools = {}

    def __init__(self, db_config: Dict):
        self.db_config = db_config

    @abstractmethod
    def get_connection(self):
        """Returns a database connection."""
        pass

class MySQLConnection(BaseDBConnection):
    """MySQL connection with connection pooling."""

    def __init__(self, db_config: Dict):
        super().__init__(db_config)

    def get_connection(self):
        """Returns a MySQL connection from the pool."""
        db_key = f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        
        if db_key not in self._connection_pools:
            self._connection_pools[db_key] = pooling.MySQLConnectionPool(
                pool_name=db_key,
                pool_size=5,  # Number of connections in the pool
                host=self.db_config["host"],
                port=self.db_config["port"],
                user=self.db_config["username"],
                password=self.db_config["password"],
                database=self.db_config["database"],
            )

        return self._connection_pools[db_key].get_connection()
