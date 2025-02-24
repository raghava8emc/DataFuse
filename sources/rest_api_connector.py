import requests
import os
from sources.base_connector import BaseConnector
from parsers.content_parser import ContentParser
from utils.logging_utils import logger
import concurrent.futures
import json

class RestAPIConnector(BaseConnector):
    def __init__(self, base_url, headers, endpoints, temp_dir):
        super().__init__("REST API")
        self.base_url = base_url
        self.headers = headers
        self.endpoints = endpoints
        self.temp_dir = temp_dir  # Use temp_dir from SourceManager

    def test_connection(self):
        """Checks if the REST API is reachable."""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                logger.info(f"Successfully connected to REST API `{self.base_url}`.")
                return True
            logger.error(f"REST API `{self.base_url}` returned status code {response.status_code}.")
            return False
        except requests.RequestException as e:
            logger.error(f"Failed to connect to REST API `{self.base_url}`: {e}")
            return False

    def fetch_endpoint(self, endpoint):
        """Fetches a single endpoint's data and saves it to a file."""
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Requesting data from {url}...")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").split(";")[0]
            logger.info(f"Detected content type: {content_type}")

            data = ContentParser.parse_response(response.text, content_type)

            # Save data to file
            file_path = os.path.join(self.temp_dir, f"{endpoint}.json")
            logger.info(f"Saving source data to tmp directory file: {file_path}")
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            return endpoint, file_path  

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return endpoint, None

    def fetch_data(self):
        """Fetches all endpoints concurrently using threads."""
        logger.info(f"Fetching data from REST API: {self.base_url}")

        data_files = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()-1) as executor:
            future_to_endpoint = {executor.submit(self.fetch_endpoint, endpoint): endpoint for endpoint in self.endpoints}

            for future in concurrent.futures.as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    _, file_path = future.result()
                    if file_path:
                        data_files[endpoint] = file_path
                        logger.info(f"Fetched and stored data for {endpoint}.")
                    else:
                        logger.error(f"Failed to fetch data for {endpoint}.")
                except Exception as e:
                    logger.error(f"Error fetching {endpoint}: {e}")

        return data_files
