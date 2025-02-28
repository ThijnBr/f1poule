import sys
import os

# Set the virtual environment path
venv_path = "/var/www/f1poule/venv"
activate_this = os.path.join(venv_path, "bin", "activate_this.py")

# Activate the virtual environment
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Add the app directory to the Python path
sys.path.insert(0, "/var/www/f1poule")

# Import the application
from app import create_app
application = create_app()

