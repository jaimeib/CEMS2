# Description: Setting schema using Pydantic ORM (Object Relational Mapper)
from typing import Optional

from pydantic import BaseModel, Field


class Setting(BaseModel):
    id: int
    key: str = Field(max_length=255)
    value: str = Field(max_length=255)
    description: Optional[str] = Field(max_length=255)

    class Config:
        orm_mode = True  # This is needed to return the model as a dictionary
