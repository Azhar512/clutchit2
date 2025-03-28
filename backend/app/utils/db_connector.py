from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config

# Create database engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create a scoped session
db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))

# Declarative base for models
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """
    Initialize the database. 
    Import all modules here that might define models so that
    they will be registered properly on the metadata.
    """
    import app.models  # Import all model modules
    Base.metadata.create_all(bind=engine)

def get_db_connection():
    """
    Get database session
    
    Returns:
        SQLAlchemy scoped session
    """
    return db_session