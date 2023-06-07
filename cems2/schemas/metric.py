"""Metric schema using Pydantic ORM (Object Relational Mapper)."""

from datetime import datetime

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """Metric schema using Pydantic ORM (Object Relational Mapper)."""

    name: str = Field(..., example="utilization")
    value: float = Field(..., example=25.5)
    unit: str = Field(..., example="%")
    hostname: str = Field(min_length=2, max_length=50, example="host1")
    timestamp: datetime = Field(default=datetime.now())
    collected_from: str = Field(min_length=1, max_length=50, example="OpenStack")
