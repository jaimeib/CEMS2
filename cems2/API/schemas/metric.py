from pydantic import BaseModel, Field


class Metric(BaseModel):
    """
    Metric schema using Pydantic ORM (Object Relational Mapper)
    """

    name: str = Field(..., example="utilization")
    value: float = Field(..., example=25)
    unit: str = Field(..., example="%")
    timestamp: str = Field(..., example="2021-01-01 12:00:00")
    hostname: str = Field(..., example="host1")
