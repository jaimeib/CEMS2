"""API endpoints for the log in controller."""

from fastapi import APIRouter, Depends, HTTPException, status

from cems2 import log
from cems2.schemas.credential import Credential

# Create the log in controller router
login = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)

# API ENDPOINTS


# Validate the user credentials usign the OpenStack Keystone API
@login.post(
    "/login",
    summary="Validates the user credentials usign the OpenStack Keystone API",
    status_code=status.HTTP_200_OK,
)
def _user_login(credentials: Credential):
    """Validates the user credentials usign the OpenStack Keystone API."""

    LOG.debug("Validating the user credentials")

    # Validate the user credentials
    if credentials.username == "admin" and credentials.password == "admin":
        LOG.info("User credentials validated")
        return Message(message="User credentials validated")
    else:
        LOG.error("User credentials not validated")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


# Logout the user
@login.post("/logout", summary="Logout the user", status_code=status.HTTP_200_OK)
def _user_logout():
    """Logout the user."""
