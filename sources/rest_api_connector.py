import requests
from sources.base_connector import BaseConnector
from parsers.content_parser import ContentParser
from config.logger_config import get_logger

logger = get_logger(__name__)

class RestAPIConnector(BaseConnector):
    def __init__(self, base_url, headers, endpoints):
        super().__init__("REST API")
        self.base_url = base_url
        self.headers = headers
        self.endpoints = endpoints

    def fetch_endpoint(self, endpoint):
        """Fetches a single endpoint's data (Runs synchronously)."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").split(";")[0]
            return endpoint, ContentParser.parse_response(response.text, content_type)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return endpoint, None

    def fetch_data(self):
        """Fetches all endpoints sequentially (single-threaded)."""
        return {endpoint: self.fetch_endpoint(endpoint)[1] for endpoint in self.endpoints}
