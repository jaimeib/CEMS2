# Description: Machine schema using Pydantic ORM (Object Relational Mapper)

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseMachine(BaseModel):
    group_name: str = Field(max_length=50)
    hostname: str = Field(..., min_length=3, max_length=50)
    model: str = Field(max_length=255)
    ip: str = Field(
        ...,
        regex="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    )
    user: str = Field(max_length=255)
    password: str = Field(max_length=255)
    status: bool = True
    available: bool = True

    class Config:
        orm_mode = True  # This is needed to return the model as a dictionary


class Machine(BaseMachine):
    machine_id: Optional[int]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    class Config:
        orm_mode = True  # This is needed to return the model as a dictionary
