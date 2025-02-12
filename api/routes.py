from fastapi import APIRouter, HTTPException
from ingestion.orchestrator import Orchestrator
from ingestion.source_manager import SourceManager  
from storage.enums import StorageType, FormatType
from pydantic import BaseModel
from typing import Dict, Union

router = APIRouter()

class IngestionRequest(BaseModel):
    source_type: str  # Can be "restapi", "sql", "sftp", etc.
    config: Dict  # Configuration for the selected source
    storage_type: Union[str, StorageType]  # Accepts string or Enum
    format_type: Union[str, FormatType]  # Accepts string or Enum
    output_config: Dict  # Output storage configuration
    validation_schema: Dict = {}  # Optional validation schema

@router.post("/ingest")
def ingest_data(request: IngestionRequest):
    """Trigger ingestion dynamically based on source type."""

    try:
        if isinstance(request.storage_type, str):
            request.storage_type = StorageType[request.storage_type.upper()]
        if isinstance(request.format_type, str):
            request.format_type = FormatType[request.format_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid storage_type or format_type provided.")

    source_manager = SourceManager()
    source = source_manager.get_connector(request.source_type, request.config)
    if not source:
        raise HTTPException(status_code=400, detail="Unsupported source type provided.")

    orchestrator = Orchestrator(
        connectors=[source],
        storage_type=request.storage_type,
        format_type=request.format_type,
        output_config=request.output_config,
        validation_schemas={request.source_type: request.validation_schema} 
    )

    orchestrator.start_ingestion()
    return {"message": "Ingestion started successfully!", "storage_type": request.storage_type.name}
