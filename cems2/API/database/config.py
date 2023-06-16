"""Configuration for the database connection."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from cems2 import config_loader

# Get the configuration
CONFIG = config_loader.get_config()

# Get the database configuration from the config file
user = CONFIG.get("database", "user")
password = CONFIG.get("database", "pass")
host = CONFIG.get("database", "host")
port = CONFIG.get("database", "port")
name = CONFIG.get("database", "name")

# Create a connection to the mysql database
DATABASE_URL = "mysql+pymysql://%s:%s@%s:%s/%s" % (user, password, host, port, name)
engine = create_engine(DATABASE_URL)

# Create a session to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the models
Base = declarative_base()


def get_db():
    """Create a database session.

    :return: Database session
    :rtype: SessionLocal
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create the database tables."""
    Base.metadata.create_all(bind=engine)
