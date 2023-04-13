# Description: Message schema for an HTTP Response

from pydantic import BaseModel


class Message(BaseModel):
    detail: str
