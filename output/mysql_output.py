from utils.logging_utils import logger
from sqlalchemy import create_engine, Column, Integer, String, JSON, TIMESTAMP, Table, MetaData, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Any
from sqlalchemy import Text

class MySQLOutput:
    """Handles storing ingested data into dynamically created MySQL tables using SQLAlchemy."""

    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.table_names = db_config.get("table_names", {})

        logger.info(f"Initializing MySQL output handler for database `{db_config['database']}`.")

        if not self.test_connection():
            raise RuntimeError("MySQL connection failed. Check credentials.")

        self._ensure_database_exists()

        self.engine = self._get_engine()

        self.metadata = MetaData()
        self.tables = {}

    def _get_engine(self):
        """Creates and returns a new SQLAlchemy engine."""
        return create_engine(
            f"mysql+mysqlconnector://{self.db_config['username']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        )

    def test_connection(self):
        """
        Tests the connection to the MySQL server without specifying a database.
        Ensures credentials are valid.
        """
        try:
            temp_engine = create_engine(
                f"mysql+mysqlconnector://{self.db_config['username']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/"
            )
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL server.")
            return True
        except Exception as e:
            logger.error(f"MySQL connection test failed: {e}")
            return False

    def _ensure_database_exists(self):
        """Checks if the database exists; if not, creates it."""
        try:
            temp_engine = create_engine(
                f"mysql+mysqlconnector://{self.db_config['username']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/"
            )
            with temp_engine.connect() as connection:
                existing_databases = connection.execute(text("SHOW DATABASES;")).fetchall()
                database_names = [db[0] for db in existing_databases]

                if self.db_config["database"] not in database_names:
                    logger.info(f"Database `{self.db_config['database']}` does not exist. Creating it...")
                    connection.execute(text(f"CREATE DATABASE {self.db_config['database']}"))
                    logger.info(f"Database `{self.db_config['database']}` created successfully.")

        except Exception as e:
            logger.error(f"Error ensuring database existence: {e}")
            raise RuntimeError("Database creation failed.")


    def _infer_column_types(self, sample_record):
        """Infers column types based on sample record data."""
        columns = []
        for key, value in sample_record.items():
            column_name = key  # Keep original case for column names
            if isinstance(value, int):
                columns.append(Column(column_name, Integer))
            elif isinstance(value, float):
                columns.append(Column(column_name, String(50)))  
            elif isinstance(value, str):
                columns.append(Column(column_name, Text))  
            elif isinstance(value, (list, dict)):
                columns.append(Column(column_name, JSON))
            else:
                columns.append(Column(column_name, Text))  # Fallback to Text()

        return columns

    def _get_or_create_table(self, endpoint: str, sample_record: Dict):
        """Creates a table dynamically with column names matching JSON structure."""
        table_name = self.table_names.get(endpoint, f"{endpoint}_data")

        if table_name in self.tables:
            logger.info(f"Table {table_name} already exists.")
            return self.tables[table_name]

        logger.info(f"Creating table `{table_name}` with inferred schema...")

        dynamic_columns = self._infer_column_types(sample_record)

        table = Table(
            table_name, self.metadata,
            *dynamic_columns, 
            extend_existing=True
        )

        self.metadata.create_all(self.engine)  # Create table in MySQL
        self.tables[table_name] = table
        logger.info(f"Table `{table_name}` created successfully.")

        return table

    def save(self, data: List[Dict], source_name: str, endpoint: str):
        """Efficiently inserts data into MySQL tables using bulk insert."""
        if not data:
            logger.warning(f"No data to insert for `{endpoint}`. Skipping.")
            return

        session = sessionmaker(bind=self.engine)()

        sample_record = data[0] if isinstance(data, list) and len(data) > 0 else None
        if not sample_record:
            logger.error(f"No valid sample record found for `{endpoint}`.")
            return

        # Ensure table exists
        table = self._get_or_create_table(endpoint, sample_record)

        valid_columns = {col.name for col in table.columns}
        
        # Filter data to match table schema
        filtered_data = [{key: value for key, value in record.items() if key in valid_columns} for record in data]

        logger.info(f"Preparing to bulk insert {len(filtered_data)} records into `{endpoint}` table.")

        try:
            session.execute(table.insert(), filtered_data)
            session.commit()
            logger.info(f"Successfully inserted {len(filtered_data)} records into `{endpoint}` table.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting data into `{endpoint}`: {e}")
            raise
        finally:
            session.close()
