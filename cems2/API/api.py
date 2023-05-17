"""API endpoints for CEMS2."""

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc


from fastapi import FastAPI

from cems2 import config_loader
from cems2.API.database.loader import load_hosts
from cems2.API.routes.actions import actions
from cems2.API.routes.login import login
from cems2.API.routes.machine import machines
from cems2.API.routes.monitoring import monitoring

# Obtain the configuration
CONFIG = config_loader.get_config()

# Create the FastAPI app
api = FastAPI(
    title="CEMS2 REST API",
    description="REST API for the CEMS2 project",
    version="0.1.0",
)

# Load the initial data .yaml file into the database
load_hosts(CONFIG.get("data", "file"))

# Include the login router
api.include_router(login, tags=["Log In Controller"])

# Include the machines manager router
api.include_router(machines, tags=["Machine Manager"])

# Include the actions controller router
api.include_router(actions, tags=["Actions Controller"])

# Include the monitoring controller router
api.include_router(monitoring, tags=["Monitoring Controller"])
