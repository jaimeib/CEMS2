from database.config import Base
from sqlalchemy.schema import Column, Table
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String


class Machines(Base):
    """
    Machine model usign SQLAlchemy ORM (Object Relational Mapper)
    """

    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    groupname = Column(String(50), nullable=False)
    hostname = Column(String(50), nullable=False, unique=True, index=True)
    brand_model = Column(String(255), nullable=False)
    management_ip = Column(String(16), nullable=False, unique=True)
    management_username = Column(String(255), nullable=False)
    management_password = Column(String(255), nullable=False)
    energy_status = Column(
        Boolean, nullable=True
    )  # This is the energy status of the machine (True = ON, False = OFF)
    monitoring = Column(
        Boolean, nullable=False, default=False
    )  # This is the monitoring status of the machine (True = Monitored, False = Unmonitored)
    available = Column(
        Boolean, nullable=False, default=True
    )  # This is the availability status of the machine (True = Available, False = Unavailable)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
