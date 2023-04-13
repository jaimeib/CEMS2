# Description: Machine schema using Pydantic ORM (Object Relational Mapper)

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseMachine(BaseModel):
    groupname: str = Field(max_length=50)
    hostname: str = Field(min_length=2, max_length=50)
    brand_model: str = Field(max_length=255)
    management_ip: str = Field(
        regex="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    )
    management_username: str = Field(max_length=255)
    management_password: str = Field(max_length=255)
    monitoring: bool = False  # By default, the machine is unmonitored
    available: bool = True  # By default, the machine is available

    class Config:
        orm_mode = True  # This is needed to return the model as a dictionary


class Machine(BaseMachine):
    id: Optional[int]
    energy_status: Optional[bool]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    class Config:
        orm_mode = True  # This is needed to return the model as a dictionary
