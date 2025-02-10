import logging
import os
import yaml

# Load configuration
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

log_dir = os.path.dirname(config["logging"]["log_file"])
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(config["logging"]["level"]),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(config["logging"]["log_file"]),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)