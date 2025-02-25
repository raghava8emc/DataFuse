import os
import queue
import json
import threading
import concurrent.futures
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError,ProgrammingError, SQLAlchemyError, NoSuchTableError
from utils.logging_utils import logger
from pathlib import Path

class PostgreSQLConnector:
    """
    A scalable PostgreSQL Connector with connection pooling and error handling.
    """

    def __init__(self, host, port, username, password, database, table_names, temp_dir, pool_size=8):
        """
        Initializes the PostgreSQL Connector with connection validation and a connection pool.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.table_names = table_names
        self.temp_dir = temp_dir
        self.max_connections = min(pool_size, os.cpu_count())
        self.connection_pool = queue.Queue(self.max_connections)
        self.valid_tables = set()
        self.metadata = MetaData()
        
        try:
            self._validate_connection()
            self._initialize_connection_pool()
        except OperationalError as e:
            logger.error(f"PostgreSQL Connection Error: {e}")
            raise RuntimeError(f"Failed to connect to PostgreSQL: {e}")
        
    def test_connection(self):
        """Validates PostgreSQL connection and checks if the database exists."""
        return self._validate_connection()

    def _validate_connection(self):
        """
        Validates the PostgreSQL database connection and ensures the database exists.
        """
        try:
            engine = self._create_engine()

            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}'")).fetchone()
                if not result:
                    logger.error(f"Database `{self.database}` does not exist on `{self.host}:{self.port}`.")
                    return False

                # Test basic connectivity
                conn.execute(text("SELECT 1"))  

            logger.info(f"Successfully connected to PostgreSQL database `{self.database}`.")
            return True

        except OperationalError as e:
            logger.error(f"Failed to connect to PostgreSQL `{self.host}:{self.port}`. Check username/password: {e}")
            return False

        except ProgrammingError as e:
            logger.error(f"PostgreSQL database `{self.database}` does not exist or has insufficient permissions: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error connecting to PostgreSQL `{self.host}:{self.port}`: {e}")
            return False

    def _validate_tables(self):
        """
        Validates that the specified tables exist in the database.
        Stores valid table names to avoid repeated checks.
        """
        try:
            engine = self._get_connection()
            inspector = inspect(engine)
            available_tables = inspector.get_table_names()
            self.valid_tables = {table for table in self.table_names if table in available_tables}
            missing_tables = set(self.table_names) - self.valid_tables
            
            if missing_tables:
                logger.warning(f"The following tables do not exist: {missing_tables}")
            
            self._release_connection(engine)
        except Exception as e:
            logger.error(f"Error validating tables: {e}")
            raise RuntimeError("Table validation failed.")
    
    def _initialize_connection_pool(self):
        """
        Pre-creates connections and stores them in the pool.
        """
        logger.info(f"Initializing PostgreSQL connection pool with {self.max_connections} connections...")
        for _ in range(self.max_connections):
            try:
                self.connection_pool.put(self._create_engine())
            except OperationalError as e:
                logger.error(f"PostgreSQL Connection Error: {e}")
                raise RuntimeError(f"Could not create PostgreSQL connections: {e}")

    def _create_engine(self):
        """
        Creates a new SQLAlchemy engine for PostgreSQL.
        """
        try:
            return create_engine(
                f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}",
                pool_size=self.max_connections,
                max_overflow=2,
                pool_pre_ping=True
            )
        except OperationalError as e:
            logger.error(f"Connection to PostgreSQL failed: {e}")
            raise RuntimeError(f"Could not connect to PostgreSQL database: {e}")
    
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

    def _prepare_for_ingestion(self):
        """Ensures tables exist before ingestion begins."""
        if not self.valid_tables:
            self._validate_tables()

    def fetch_table_data(self, table_name):
        """
        Fetches data from a PostgreSQL table and stores it in the temp directory.
        """
        if table_name not in self.valid_tables:
            logger.error(f"Table `{table_name}` does not exist in `{self.database}`.")
            return None

        engine = self._get_connection()
        session = sessionmaker(bind=engine)()

        try:
            logger.info(f"Fetching data from `{table_name}`...")
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
            query = session.query(table).yield_per(1000)  # Efficient for large tables
            data = [dict(row._asdict()) for row in query]
            session.close()

            if not data:
                logger.warning(f"No data found in `{table_name}`.")
                self._release_connection(engine)
                return None

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
        logger.info(f"Fetching data from PostgreSQL database `{self.database}`...")
        downloaded_files = {}
        self._prepare_for_ingestion()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_table = {executor.submit(self.fetch_table_data, table): table for table in self.valid_tables}
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
        return downloaded_files