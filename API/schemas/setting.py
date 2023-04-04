# Description: Setting schema using Pydantic ORM (Object Relational Mapper)
from typing import Optional

from pydantic import BaseModel, Field


class BaseSetting(BaseModel):
    key: str = Field(max_length=50)
    value: str = Field(max_length=255)
    description: Optional[str] = Field(max_length=255)

    class Config:
        orm_mode = True  # This is needed to return the model as a dictionary


class Setting(BaseSetting):
    id: Optional[int]
    created_at: Optional[str]
    modified_at: Optional[str]

    class Config:
        orm_mode = True
