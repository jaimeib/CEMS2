"""
FastAPI app using the routers from the API/routes folder to create the API endpoints for CEMS2
"""

from database.loader import load_hosts
from fastapi import FastAPI
from routes.actions import actions
from routes.login import login
from routes.machine import machines
from routes.monitoring import monitoring

# Create the FastAPI app
api = FastAPI(
    title="CEMS2 REST API",
    description="REST API for the CEMS2 project",
    version="0.1.0",
)

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc

# Load the initial data .yaml file into the database
load_hosts()

# Include the login router
api.include_router(login, tags=["Log In Controller"])

# Include the machines manager router
api.include_router(machines, tags=["Machine Manager"])

# Include the actions controller router
api.include_router(actions, tags=["Actions Controller"])

# Include the monitoring controller router
api.include_router(monitoring, tags=["Monitoring Controller"])
