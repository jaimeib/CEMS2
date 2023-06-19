"""Plugin schema using Pydantic ORM (Object Relational Mapper)."""

from pydantic import BaseModel, Field


class Plugin(BaseModel):
    """Plugin schema using Pydantic ORM (Object Relational Mapper)."""

    name: str = Field(..., example="Utilization")
    type: str = Field(..., example="Collector")
    status: str = Field(..., example="Installed")
