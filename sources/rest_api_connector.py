import requests
import time
from sources.base_connector import BaseConnector
from config.logger_config import get_logger

logger = get_logger(__name__)

class RestAPIConnector(BaseConnector):
    def __init__(self, base_url, headers, endpoints, retry_attempts=3, retry_delay=2):
        super().__init__("REST API")
        self.base_url = base_url
        self.headers = headers
        self.endpoints = endpoints
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
    
    def fetch_data(self):
        results = {}
        for endpoint in self.endpoints:
            url = f"{self.base_url}/{endpoint}"
            attempts = 0
            while attempts < self.retry_attempts:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    logger.info(f"Successfully fetched data from {url}")
                    results[endpoint] = response.json()
                    break  # Exit retry loop on success
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error fetching {url}: {e}. Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay * (2 ** attempts))  # Exponential backoff
                    attempts += 1
            if attempts == self.retry_attempts:
                logger.error(f"Failed to fetch {url} after {self.retry_attempts} attempts.")
                results[endpoint] = None
        return results