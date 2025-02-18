import requests
from sources.base_connector import BaseConnector
from parsers.content_parser import ContentParser
from utils.logging_utils import logger
import concurrent.futures
import os

class RestAPIConnector(BaseConnector):
    def __init__(self, base_url, headers, endpoints):
        super().__init__("REST API")
        self.base_url = base_url
        self.headers = headers
        self.endpoints = endpoints

    def fetch_endpoint(self, endpoint):
        """Fetches a single endpoint's data with proper content handling."""
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Requesting data from {url}...")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").split(";")[0]
            logger.info(f"Detected content type: {content_type}")

            # Handle binary responses separately
            if "image" in content_type or "octet-stream" in content_type:
                return endpoint, response.content  # Return raw binary data

            # Parse response for known textual formats
            return endpoint, ContentParser.parse_response(response.text, content_type)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return endpoint, None

    def fetch_data(self):
        """Fetches all endpoints concurrently using threads (I/O-bound)."""
        logger.info(f"Fetching data from REST API: {self.base_url}")

        data = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()-1) as executor:
            future_to_endpoint = {executor.submit(self.fetch_endpoint, endpoint): endpoint for endpoint in self.endpoints}

            for future in concurrent.futures.as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    _, content = future.result()  
                    if content is not None:
                        data[endpoint] = content 
                        logger.info(f"Fetched data for {endpoint} successfully.")
                    else:
                        logger.error(f"Failed to fetch data for {endpoint}.")
                except Exception as e:
                    logger.error(f"Error fetching {endpoint}: {e}")
        return data  
    
