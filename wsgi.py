import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the create_app function
from backend.app import create_app

# Create the Flask application
app = create_app()

# For WSGI servers like Gunicorn
application = app

if __name__ == "__main__":
    app.run()
