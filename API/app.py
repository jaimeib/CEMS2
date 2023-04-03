# Description: FastAPI app using the routers from the API/routes folder

from fastapi import FastAPI
from routes.machine import machines
from routes.setting import settings

# Create the FastAPI app
app = FastAPI(
    title="Energy Management System API",
    description="REST API for the Energy Management System",
    version="0.1.0",
)

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation con Swagger UI: http://localhost:8000/docs
# Documentacion con ReDoc: http://localhost:8000/redoc

# Include the machines router
app.include_router(machines, tags=["Machine Persistence Manager"])

# Include the settings router
app.include_router(settings, tags=["Settings Manager"])
