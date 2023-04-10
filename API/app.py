# Description: FastAPI app using the routers from the API/routes folder

from database.config import create_tables
from fastapi import FastAPI
from routes.machine import machines

# Create the FastAPI app
app = FastAPI(
    title="Energy Management System API",
    description="REST API for the Energy Management System",
    version="0.1.0",
)

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation and tester with Swagger UI: http://localhost:8000/docs
# Documentation with ReDoc: http://localhost:8000/redoc

# Create the databases tables (if they don't exist)
create_tables()

# Include the machines router
app.include_router(machines, tags=["Machine Persistence Manager"])
