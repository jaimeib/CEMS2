"""Metric schema using Pydantic ORM (Object Relational Mapper)."""


from datetime import datetime

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """Metric schema using Pydantic ORM (Object Relational Mapper)."""

    name: str = Field(..., example="vms")
    payload: str = Field(
        ...,
        example={
            "uuid1": {
                "vcpus": 2,
                "memory": {"amount": 2048, "unit": "MB"},
                "disk": {"amount": 20, "unit": "GB"},
                "managed_by": "OpenStack",
            },
            "uuid2": {
                "vcpus": 4,
                "memory": {"amount": 4096, "unit": "MB"},
                "disk": {"amount": 40, "unit": "GB"},
                "managed_by": "OpenStack",
            },
        },
    )
    hostname: str = Field(min_length=2, max_length=50, example="host1")
    timestamp: datetime = Field(default=datetime.now())
    collected_from: str = Field(min_length=1, max_length=50, example="OpenStackVMs")
