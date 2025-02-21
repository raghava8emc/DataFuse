import os
import queue
import json
import threading
import concurrent.futures
from pymongo import MongoClient, errors
from utils.logging_utils import logger
from pathlib import Path

class MongoDBConnector:
    """A scalable MongoDB Connector with connection pooling and optimized connection handling."""

    def __init__(self, host, port, username, password, database, collection_names, temp_dir, pool_size=8):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.collection_names = collection_names
        self.temp_dir = temp_dir
        self.max_connections = min(pool_size, os.cpu_count())

        self._validate_connection()
        self.connection_pool = queue.Queue(self.max_connections)
        self._initialize_connection_pool()

    def _validate_connection(self):
        """Checks MongoDB connectivity and authentication."""
        try:
            client = MongoClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                serverSelectionTimeoutMS=5000
            )
            db = client[self.database]

            if self.database not in client.list_database_names():
                raise RuntimeError(f"Database `{self.database}` does not exist.")

            logger.info(f"Successfully connected to MongoDB `{self.database}`.")
            client.close()
        except errors.ServerSelectionTimeoutError:
            logger.error(f"Failed to connect to MongoDB at `{self.host}:{self.port}`.")
            raise
        except errors.OperationFailure as e:
            logger.error(f"MongoDB authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while connecting to MongoDB: {e}")
            raise

    def _initialize_connection_pool(self):
        """Pre-creates connections for efficient querying."""
        logger.info(f"Initializing MongoDB connection pool with {self.max_connections} connections...")
        for _ in range(self.max_connections):
            self.connection_pool.put(self._create_connection())

    def _create_connection(self):
        """Creates a new MongoDB client."""
        return MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )

    def _get_connection(self):
        """Retrieves a connection from the pool."""
        client = self.connection_pool.get()
        logger.info(f"Retrieved a MongoDB connection from the pool.")
        return client

    def _release_connection(self, client):
        """Returns the connection back to the pool."""
        self.connection_pool.put(client)
        logger.info(f"Released MongoDB connection back to the pool.")

    def fetch_collection_data(self, collection_name):
        """Fetches data from MongoDB and streams it to a file."""
        client = self._get_connection()
        db = client[self.database]

        try:
            logger.info(f"Fetching data from `{collection_name}`...")

            if collection_name not in db.list_collection_names():
                logger.error(f"Collection `{collection_name}` does not exist.")
                return None

            collection = db[collection_name]

            # Stream data instead of loading in memory
            cursor = collection.find({}, {"_id": 0})  # Exclude `_id`

            os.makedirs(self.temp_dir, exist_ok=True)
            file_path = Path(self.temp_dir) / f"{collection_name}.json"

            with file_path.open("w", encoding="utf-8") as file:
                file.write("[")  # Start JSON array
                first = True
                for doc in cursor:
                    if not first:
                        file.write(",\n")  # Add a comma between documents
                    json.dump(doc, file)
                    first = False
                file.write("]")  # Close JSON array

            logger.info(f"Data from `{collection_name}` saved to `{file_path}`.")

            return collection_name, str(file_path)

        except errors.PyMongoError as e:
            logger.error(f"MongoDB error fetching `{collection_name}`: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching `{collection_name}`: {e}")
        finally:
            self._release_connection(client)  # Ensure connection is always released

        return None

    def fetch_data(self):
        """Fetches data from all specified collections using multithreading."""
        logger.info(f"Fetching data from MongoDB `{self.database}`...")

        downloaded_files = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_collection = {
                executor.submit(self.fetch_collection_data, collection): collection 
                for collection in self.collection_names
            }

            for future in concurrent.futures.as_completed(future_to_collection):
                collection_name = future_to_collection[future]
                try:
                    result = future.result()
                    if result:
                        collection, file_path = result
                        downloaded_files[collection] = file_path
                except Exception as e:
                    logger.error(f"Error processing `{collection_name}`: {e}")

        logger.info("Completed fetching all requested collections.")
        return downloaded_files
