import logging
import os

# Define log file paths
log_directory = "logs"  # Store logs in a separate directory
os.makedirs(log_directory, exist_ok=True)  # Ensure directory exists

ingestion_log_file = os.path.join(log_directory, "ingestion.log")
request_log_file = os.path.join(log_directory, "request.log")

# ---------------------- 1️⃣ General Logger (ingestion.log) ----------------------
logging.basicConfig(
    level=logging.INFO,  # Capture INFO and above messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(ingestion_log_file),  # File handler for ingestion log
        logging.StreamHandler()  # Logs to console
    ]
)
logger = logging.getLogger("IngestionPipeline")

# ---------------------- 2️⃣ Request Logger (request.log) ----------------------
request_logger = logging.getLogger("RequestLogger")
request_logger.setLevel(logging.INFO)

# Create file handler for request log
request_file_handler = logging.FileHandler(request_log_file)
request_file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

# Add handler to request logger
request_logger.addHandler(request_file_handler)

# ---------------------- 🔹 Example Usage 🔹 ----------------------