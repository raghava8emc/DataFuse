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


@router.post("/validate")
def validate_sources(request: IngestionRequest):
    """Validates source & output configuration before ingestion (No temp_dir, No DB connections)."""

    logger.info(f"🔍 Validating `{request.source_type}` → `{request.storage_type}`...")
    request_logger.info(f"VALIDATION REQUEST: {request}")

    try:
        # Convert storage_type & format_type to ENUM (if strings)
        request.storage_type = StorageType[request.storage_type.upper()] if isinstance(request.storage_type, str) else request.storage_type
        request.format_type = FormatType[request.format_type.upper()] if isinstance(request.format_type, str) else request.format_type

    except KeyError as e:
        logger.error(f"Invalid storage_type or format_type: {e}")
        return {"message": "FAILED: Invalid storage_type or format_type provided.", "error": str(e)}

    try:
        # Get Source Connector (No temp_dir creation)
        source_manager = SourceManager()
        source = source_manager.get_connector(request.source_type, request.config, request.storage_type, create_temp_dir=False)
        if not source:
            raise ValueError(f"Unsupported source type: {request.source_type}")

        # Initialize Orchestrator (No temp_dir, No DB connections)
        orchestrator = Orchestrator(
            connectors=[source],
            storage_type=request.storage_type,
            format_type=request.format_type,
            output_config=request.output_config,
            temp_dir=None,  # No temp_dir during validation
            validation_schemas={request.source_type: request.validation_schema},
            enable_db_connections=False  # Prevent DB connections during validation
        )

        # Run Validation (Input & Output)
        if not orchestrator.validate_sources():
            return {"message": "FAILED: Validation failed.", "validation_passed": False}

        return {"message": "SUCCESS: Validation successful!", "validation_passed": True}

    except ValueError as ve:
        logger.error(f"Validation Error: {ve}")
        return {"message": "FAILED: Validation error.", "error": str(ve)}

    except Exception as e:
        logger.error(f"🚨 Unexpected Error During Validation: {e}")
        return {"message": "FAILED: An unexpected error occurred.", "error": str(e)}

###  **Step 2: Start Ingestion (Only After Validation)**
@router.post("/ingest")
def ingest_data(request: IngestionRequest):
    """Starts ingestion process after successful validation."""

    logger.info(f"Received ingestion request: `{request.source_type}` → `{request.storage_type}`")
    request_logger.info(f"INGESTION REQUEST: {request}")

    try:
        # Convert storage_type & format_type to ENUM (if strings)
        request.storage_type = StorageType[request.storage_type.upper()] if isinstance(request.storage_type, str) else request.storage_type
        request.format_type = FormatType[request.format_type.upper()] if isinstance(request.format_type, str) else request.format_type

    except KeyError as e:
        logger.error(f"Invalid storage_type or format_type: {e}")
        return {"message": "FAILED: Invalid storage_type or format_type provided.", "error": str(e)}

    try:
        # Get Source Connector (Temp dir created for ingestion)
        source_manager = SourceManager()
        source = source_manager.get_connector(request.source_type, request.config, request.storage_type, create_temp_dir=True)
        if not source:
            raise ValueError(f"Unsupported source type: {request.source_type}")

        # Initialize Orchestrator (Temp dir enabled for ingestion)
        orchestrator = Orchestrator(
            connectors=[source],
            storage_type=request.storage_type,
            format_type=request.format_type,
            output_config=request.output_config,
            temp_dir=source_manager.temp_dir,  # Temp directory only for ingestion
            validation_schemas={request.source_type: request.validation_schema},
            enable_db_connections=True  # Enable DB connections for ingestion
        )

        logger.info(f"Starting Ingestion...")

        # Start Data Ingestion
        orchestrator.start_ingestion()

        logger.info(f"Ingestion completed successfully!")
        return {"message": "SUCCESS: Ingestion completed successfully!"}

    except ValueError as ve:
        logger.error(f"Ingestion Error: {ve}")
        return {"message": "FAILED: Ingestion error.", "error": str(ve)}

    except Exception as e:
        logger.error(f"🚨 Unexpected Error During Ingestion: {e}")
        return {"message": "FAILED: An unexpected error occurred during ingestion.", "error": str(e)}
