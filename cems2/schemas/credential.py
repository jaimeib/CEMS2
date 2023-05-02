"""Log In Credential schema using Pydantic ORM."""

from pydantic import BaseModel, Field


class Credential(BaseModel):
    """Log In Credential schema using Pydantic ORM."""

    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin")
