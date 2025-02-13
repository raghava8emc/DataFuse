import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logging_utils import logger
from typing import Dict, List


class MongoDBOutput:
    """Handles storing ingested data into MongoDB collections using multiprocessing."""

    def __init__(self, db_config: Dict):
        """
        Initializes MongoDB connection and sets up the target database.
        This ensures each process has its own connection.
        :param db_config: Dictionary containing MongoDB connection details.
        """
        self.db_config = db_config
        self.db_name = db_config.get("database", "ingestion_db")
        self.collection_names = db_config.get("collection_names", {})  # Maps endpoints to collections

        logger.info(f"Initializing MongoDBOutput for database: {self.db_name}")

    def _get_client(self):
        """
        Creates and returns a new MongoDB client.
        Ensures each process has a separate connection.
        """
        return MongoClient(
            host=self.db_config["host"],
            port=int(self.db_config["port"]),
            username=self.db_config.get("username"),
            password=self.db_config.get("password"),
            authSource="admin" if self.db_config.get("username") else None
        )

    def _get_collection(self, client, endpoint: str):
        """
        Retrieves or creates a MongoDB collection dynamically.
        Each process handles a single endpoint, so this is efficient.
        :param client: MongoDB client instance.
        :param endpoint: The API endpoint used as the collection name.
        :return: MongoDB collection object.
        """
        db = client[self.db_name]
        collection_name = self.collection_names.get(endpoint, f"{endpoint}_data")

        if collection_name not in db.list_collection_names():
            logger.info(f"Creating collection `{collection_name}` in `{self.db_name}` database.")

        return db[collection_name]

    def save(self, data: List[Dict], source_name: str, endpoint: str):
        """
        Inserts data into MongoDB collections dynamically.
        Each process will call this method separately for its assigned endpoint.
        
        :param data: List of dictionaries representing the data.
        :param source_name: Name of the data source.
        :param endpoint: The API endpoint name used to determine collection name.
        """
        if not data:
            logger.warning(f"No data to insert for `{endpoint}`. Skipping.")
            return

        client = self._get_client()  # Get a fresh connection for this process
        collection = self._get_collection(client, endpoint)

        try:
            collection.insert_many(data)
            logger.info(f"Inserted {len(data)} records into `{endpoint}` collection.")
        except PyMongoError as e:
            logger.error(f"Error inserting data into `{endpoint}` collection: {e}")
            raise e
        finally:
            client.close()  # Ensure the connection is closed after the process finishes
