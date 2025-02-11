## **Updated API Router to Use Orchestrator with Local Output Handling**

from fastapi import APIRouter
from ingestion.orchestrator import Orchestrator
from storage.enums import StorageType, FormatType
from sources.rest_api_connector import RestAPIConnector
from pydantic import BaseModel
from typing import List, Dict, Union

router = APIRouter()

class IngestionRequest(BaseModel):
    source_type: str  # Can be "restapi", "sql", "sftp", etc.
    config: Dict  # Configuration for the selected source
    storage_type: Union[str, StorageType]  # Accepts string or Enum
    format_type: Union[str, FormatType]  # Accepts string or Enum
    output_config: Dict  # Output storage configuration

@router.post("/ingest")
def ingest_data(request: IngestionRequest):
    """Trigger ingestion dynamically based on source type."""
    source = None
    
    try:
        if isinstance(request.storage_type, str):
            request.storage_type = StorageType[request.storage_type.upper()]
        if isinstance(request.format_type, str):
            request.format_type = FormatType[request.format_type.upper()]
    except KeyError:
        return {"error": "Invalid storage_type or format_type provided."}

    if request.source_type == "restapi":
        source = RestAPIConnector(
            request.config["base_url"],
            request.config["headers"],
            request.config["endpoints"]
        )

    if source:
        orchestrator = Orchestrator(
            connectors=[source],
            storage_type=request.storage_type,
            format_type=request.format_type,
            output_config=request.output_config
        )
        orchestrator.start_ingestion()
        return {"message": "Ingestion started successfully!", "storage_type": request.storage_type.name}
    else:
        return {"error": "Invalid request parameters"}