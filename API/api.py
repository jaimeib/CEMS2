# Description: FastAPI app using the routers from the API/routes folder
from database.loader import load_hosts
from fastapi import FastAPI
from log import logger
from routes.machine import machines

# Create the FastAPI app
api = FastAPI(
    title="Energy Management System API",
    description="REST API for the Energy Management System",
    version="0.1.0",
)

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc

# Load the hosts.yaml file into the database
load_hosts()

# Include the machines router
api.include_router(machines, tags=["Machine Persistence Manager"])
