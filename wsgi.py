import sys
import os

# Set the project directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the Flask application
from backend.app import create_app

# Create the Flask app instance
app = create_app()

# For Gunicorn
application = app

if __name__ == "__main__":
    app.run()
