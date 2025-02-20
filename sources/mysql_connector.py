import os
import queue
import json
import threading
import concurrent.futures
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError, NoSuchTableError
from utils.logging_utils import logger
from pathlib import Path

class MySQLConnector:
    """
    A scalable MySQL Connector with connection pooling and error handling.
    """

    def __init__(self, host, port, username, password, database, table_names, temp_dir, pool_size=8):
        """
        Initializes the MySQL Connector with a connection pool.

        Args:
        - host (str): MySQL server hostname.
        - port (int): MySQL server port.
        - username (str): MySQL username.
        - password (str): MySQL password.
        - database (str): Database name.
        - table_names (list): List of tables to fetch data from.
        - temp_dir (str): Local temporary directory for storing fetched data.
        - pool_size (int, optional): Maximum number of connections in the pool (default: 8).
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.table_names = table_names
        self.temp_dir = temp_dir

        # Define connection pool size based on CPU count (up to 8)
        self.max_connections = min(pool_size, os.cpu_count())
        self.connection_pool = queue.Queue(self.max_connections)

        # Initialize connection pool
        try:
            self._initialize_connection_pool()
            self.metadata = MetaData()
        except OperationalError as e:
            logger.error(f"MySQL Connection Error: {e}")
            raise RuntimeError(f"Failed to connect to MySQL: {e}")

    def _initialize_connection_pool(self):
        """
        Pre-creates connections and stores them in the pool.
        """
        logger.info(f"Initializing MySQL connection pool with {self.max_connections} connections...")
        for _ in range(self.max_connections):
            try:
                self.connection_pool.put(self._create_engine())
            except OperationalError as e:
                logger.error(f"MySQL Connection Error: {e}")
                raise RuntimeError(f"Could not create MySQL connections: {e}")

    def _create_engine(self):
        """
        Creates a new SQLAlchemy engine.
        """
        try:
            return create_engine(
                f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}",
                pool_size=self.max_connections,
                max_overflow=2,
                pool_pre_ping=True
            )
        except OperationalError as e:
            logger.error(f"Connection to MySQL failed: {e}")
            raise RuntimeError(f"Could not connect to MySQL database: {e}")

    def _get_connection(self):
        """
        Retrieves a connection from the pool (blocking if none are available).
        """
        return self.connection_pool.get()

    def _release_connection(self, engine):
        """
        Returns the connection back to the pool.
        """
        self.connection_pool.put(engine)

    def fetch_table_data(self, table_name):
        """
        Fetches data from a PostgreSQL table and stores it in the temp directory.
        """
        engine = self._get_connection()
        session = sessionmaker(bind=engine)()

        try:
            logger.info(f"Fetching data from `{table_name}`...")

            inspector = inspect(engine)
            if not inspector.has_table(table_name):
                logger.error(f"Table `{table_name}` does not exist in `{self.database}`.")
                self._release_connection(engine)
                return None

            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)

            query = session.query(table).yield_per(1000)  # Efficient for large tables
            data = [dict(row._asdict()) for row in query]
            session.close()  # Release DB session

            if not data:
                logger.warning(f"No data found in `{table_name}`.")
                self._release_connection(engine)
                return None

            # Save to temp_dir as JSON
            os.makedirs(self.temp_dir, exist_ok=True)
            file_path = Path(self.temp_dir) / f"{table_name}.json"

            with file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            logger.info(f"Data from `{table_name}` saved to `{file_path}`.")
            self._release_connection(engine)
            return table_name, str(file_path)

        except Exception as e:
            logger.error(f"Error fetching `{table_name}`: {e}")
            session.close()
            self._release_connection(engine)
            return None

    def fetch_data(self):
        """
        Fetches data from all specified tables using multithreading.
        """
        logger.info(f"Fetching data from MySQL database `{self.database}`...")

        downloaded_files = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_table = {executor.submit(self.fetch_table_data, table): table for table in self.table_names}

            for future in concurrent.futures.as_completed(future_to_table):
                table_name = future_to_table[future]
                try:
                    result = future.result()
                    if result:
                        table, file_path = result
                        downloaded_files[table] = file_path
                except Exception as e:
                    logger.error(f"Error processing `{table_name}`: {e}")

        logger.info("Completed fetching all requested tables.")
        return downloaded_files  # Returns {table_name: file_path}
