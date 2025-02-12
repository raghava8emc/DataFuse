from sources.rest_api_connector import RestAPIConnector

class SourceManager:
    """Manages different data source connectors dynamically."""
    
    def get_connector(self, source_type: str, config: dict):
        """Returns the appropriate source connector based on input."""
        if source_type == "restapi":
            return RestAPIConnector(
                config["base_url"],
                config["headers"],
                config["endpoints"]
            )
        
        return None