from flask import send_from_directory
from dotenv import load_dotenv
import os
import click
from flask.cli import FlaskGroup
from app import create_app, db  # Import create_app from __init__.py

# Load environment variables
load_dotenv()

# Create a CLI group for additional commands
@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the Clutch App."""
    pass

@cli.command("create-tables")
def create_tables():
    """Create database tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        click.echo("Database tables created successfully!")

@cli.command("drop-tables")
def drop_tables():
    """Drop all database tables."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        click.echo("All database tables dropped!")

@cli.command("reset-database")
def reset_database():
    """Drop and recreate all database tables."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        click.echo("Database reset successfully!")

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=os.getenv("FLASK_DEBUG", "True") == "True", 
        host='0.0.0.0', 
        port=int(os.getenv("PORT", 5000))
    )
