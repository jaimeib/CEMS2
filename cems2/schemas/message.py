"""Message to HHTP responses schema using Pydantic ORM (Object Relational Mapper)."""

from pydantic import BaseModel


class Message(BaseModel):
    """Message to HHTP responses schema using Pydantic ORM (Object Relational Mapper)."""

    message: str
