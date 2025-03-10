import os
from backend.app import create_app

# Set the default environment if not already set
os.environ.setdefault("FLASK_ENV", "production")

# Create the Flask application
app = create_app()

# For WSGI servers like Gunicorn
application = app

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "False") == "True", host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
