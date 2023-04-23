import log
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.message import Message

# Create the actions controller router
actions = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)

# Get the possible actions to apply to the cloud infrastructure
