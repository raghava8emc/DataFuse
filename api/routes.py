from fastapi import APIRouter, HTTPException
from ingestion.orchestrator import Orchestrator
from ingestion.source_manager import SourceManager  
from storage.enums import StorageType, FormatType
from pydantic import BaseModel
from typing import Dict, Union, Optional
from utils.logging_utils import logger
from utils.logging_utils import request_logger



router = APIRouter()

class IngestionRequest(BaseModel):
    source_type: str  # Example: "restapi"
    config: Dict  # Config for source (URL, headers, endpoints, etc.)
    storage_type: Union[str, StorageType]  # Example: "local", "mysql", etc.
    format_type: Union[str, FormatType]  # JSON or CSV (For local), JSON (For DBs)
    output_config: Dict  # Output details (DB credentials or Local path)
    validation_schema: Optional[Dict] = {}  # Default empty schema

@router.post("/ingest")
def ingest_data(request: IngestionRequest):
    """Trigger ingestion dynamically based on user input."""

    logger.info(f"Received request for ingestion with source: {request.source_type}")
    request_logger.info(f"REQUEST BODY  : {request}")
    # Convert storage_type & format_type to ENUM if they are strings
    try:
        if isinstance(request.storage_type, str):
            request.storage_type = StorageType[request.storage_type.upper()]
        if isinstance(request.format_type, str):
            request.format_type = FormatType[request.format_type.upper()]
    except KeyError:
        logger.error("Invalid storage_type or format_type provided.")
        raise HTTPException(status_code=400, detail="Invalid storage_type or format_type provided.")

    # Validate Local Storage format type (Should be JSON or CSV only)
    if request.storage_type == StorageType.LOCAL and request.format_type not in {FormatType.JSON, FormatType.CSV}:
        logger.error("Invalid format type for local storage. Must be JSON or CSV.")
        raise HTTPException(status_code=400, detail="Invalid format type for local storage. Must be JSON or CSV.")

    # Validate Database Storage (Format must be JSON)
    if request.storage_type != StorageType.LOCAL and request.format_type != FormatType.JSON:
        logger.error("Databases only support JSON format.")
        raise HTTPException(status_code=400, detail="Databases only support JSON format.")

    # Validate Source Connector
    source_manager = SourceManager()
    source = source_manager.get_connector(request.source_type, request.config)
    if not source:
        logger.error(f"Unsupported source type: {request.source_type}")
        raise HTTPException(status_code=400, detail="Unsupported source type provided.")

    # Initialize Orchestrator
    orchestrator = Orchestrator(
        connectors=[source],
        storage_type=request.storage_type,
        format_type=request.format_type,
        output_config=request.output_config,
        temp_dir=source_manager.temp_dir,
        validation_schemas={request.source_type: request.validation_schema}
    )

    # Start Data Ingestion
    logger.info("Starting ingestion process...")
    orchestrator.start_ingestion()
    request_logger.info("Ingestion completed successfully!")
    logger.info("Ingestion completed successfully!\n")

    return {"message": "Ingestion completed successfully!", "storage_type": request.storage_type.name}
