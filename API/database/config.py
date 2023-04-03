# Description: This file contains the configuration for the database connection

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a connection to the mysql database
DATABASE_URL = "mysql+pymysql://root:dbpassword@localhost:3306/CPD_IFCA"
engine = create_engine(DATABASE_URL)

# Create a session to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the models
Base = declarative_base()

# Create a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create the database tables
def create_tables():
    Base.metadata.create_all(bind=engine)
