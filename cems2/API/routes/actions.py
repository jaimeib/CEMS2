"""
API endpoints for the actions controller
"""

from fastapi import APIRouter, Depends, HTTPException, status

from cems2 import log

# Create the actions controller router
actions = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)

# Get the possible actions to apply to the cloud infrastructure
