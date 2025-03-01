import os
import logging

# Get current directory (where this script is located)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the log file path inside the app directory
log_file_path = os.path.join(current_directory, "security.log")

# Configure logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

security_file_handler = logging.FileHandler(log_file_path)
security_file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
security_file_handler.setFormatter(formatter)

security_logger.addHandler(security_file_handler)

print(f"Logging to: {log_file_path}")
