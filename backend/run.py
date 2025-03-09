import sys
import os

# Append the backend directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
