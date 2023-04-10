# Description: Machine model usign SQLAlchemy ORM (Object Relational Mapper)

from database.config import Base
from sqlalchemy.schema import Column, Table
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String


# Table to store the machines
class Machines(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    groupname = Column(String(50), nullable=False)
    hostname = Column(String(50), nullable=False, unique=True, index=True)
    model = Column(String(255), nullable=False)
    ip = Column(String(16), nullable=False, unique=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
