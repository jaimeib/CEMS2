from pydantic import BaseModel


class Message(BaseModel):
    """
    Message to HHTP responses schema using Pydantic ORM (Object Relational Mapper)
    """

    detail: str
