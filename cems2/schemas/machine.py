"""Machine schemas using Pydantic ORM."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseMachine(BaseModel):
    """Base Machine schema using Pydantic ORM."""

    groupname: str = Field(max_length=50)
    hostname: str = Field(min_length=2, max_length=50)
    brand_model: str = Field(max_length=255)
    management_ip: str = Field(
        regex="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
    )
    management_username: str = Field(max_length=255)
    management_password: str = Field(max_length=255)
    monitoring: bool = False  # By default, the machine is unmonitored
    available: bool = True  # By default, the machine is available

    class Config:
        """Config class for the BaseMachine schema as a dictionary."""

        orm_mode = True  # This is needed to return the model as a dictionary


class Machine(BaseMachine):
    """Machine schema using Pydantic ORM."""

    id: Optional[int]
    energy_status: Optional[bool]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    class Config:
        """Config class for the BaseMachine schema as a dictionary."""

        orm_mode = True  # This is needed to return the model as a dictionary
