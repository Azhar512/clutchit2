import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the create_app function
from backend.app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    app.run()