from fastapi import FastAPI
from routes.machine import machine

# Create the FastAPI app
app = FastAPI()

# Start server with: uvicorn app:app --reload
# Open browser to: http://localhost:8000/

# Documentation con Swagger UI: http://localhost:8000/docs
# Documentacion con ReDoc: http://localhost:8000/redoc

# Include the machines router
app.include_router(machine)
