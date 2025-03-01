import logging
import os

# Get current directory
current_directory = os.getcwd()

# Set log file path in the current directory
log_file_path = os.path.join(current_directory, "security.log")

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
security_file_handler = logging.FileHandler(log_file_path)
security_file_handler.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
security_file_handler.setFormatter(formatter)

# Add the handler to the logger
security_logger.addHandler(security_file_handler)

print(f"Logging to: {log_file_path}")
