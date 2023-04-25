"""
Log In Credential schema using Pydantic ORM (Object Relational Mapper)
"""

from pydantic import BaseModel, Field


class Credential(BaseModel):
    """
    Log In Credential schema using Pydantic ORM (Object Relational Mapper)
    """

    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin")
