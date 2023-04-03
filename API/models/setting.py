# Description: Setting model usign SQLAlchemy ORM (Object Relational Mapper)

from database.config import Base
from sqlalchemy.schema import Column, Table
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String

# Table to store the settings


class Settings(Base):

    __tablename__ = "settings"

    setting_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(50), nullable=False, unique=True, index=True)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
