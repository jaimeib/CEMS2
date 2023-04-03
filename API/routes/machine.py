# Description: This file contains the CRUD operations for the machines table.

from cryptography.fernet import Fernet
from database.config import Base, SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException
from models.machine import Machines
from schemas.machine import Machine
from sqlalchemy.orm import Session

# Create the machines router
machine = APIRouter()

# Encrypt the passwords
key = Fernet.generate_key()
encription = Fernet(key)

# Create the databases tables
Base.metadata.create_all(bind=engine)

# Create a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD operations

# CREATE

# Create a new machine
@machine.post("/machines")
def create_machine(machine: Machine, db: Session = Depends(get_db)):

    # Create a new machine model with the data from the request
    machine_model = Machines()
    machine_model.group_name = machine.group_name
    machine_model.hostname = machine.hostname
    machine_model.model = machine.model
    machine_model.ip = machine.ip
    machine_model.user = machine.user
    machine_model.password = encription.encrypt(machine.password.encode())
    machine_model.status = machine.status
    machine_model.enable = machine.enable

    # Check if the machine already exists (by hostname)
    if db.query(Machines).filter(Machines.hostname == machine.hostname).first():
        raise HTTPException(status_code=400, detail="Machine already exists")

    # Add the machine to the database
    db.add(machine_model)
    db.commit()

    # Return the machine created
    return machine_model


# READ

# Get all the machines
@machine.get("/machines")
def get_machines(db: Session = Depends(get_db)):

    # Get all the machines from the database
    return db.query(Machines).all()


# Get a machine by machine_id
@machine.get("/machines/id/{machine_id}")
def get_machine_by_machine_id(machine_id: str, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine is None:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

    # Return the machine
    return machine


# UPDATE

# Update a machine by machine_id
@machine.put("/machines/{machine_id}")
def update_machine(machine_id: str, machine: Machine, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

    # Check if the updated data not conflict with other machines (Hostname and IP)
    if db.query(Machines).filter(Machines.hostname == machine.hostname).first():
        raise HTTPException(
            status_code=400, detail="There is another machine with the same hostname"
        )

    if db.query(Machines).filter(Machines.ip == machine.ip).first():
        raise HTTPException(
            status_code=400, detail="There is another machine with the same IP"
        )

    # Update the machine data
    machine_model.group_name = machine.group_name
    machine_model.hostname = machine.hostname
    machine_model.model = machine.model
    machine_model.ip = machine.ip
    machine_model.user = machine.user
    machine_model.password = encription.encrypt(machine.password.encode())
    machine_model.status = machine.status
    machine_model.enable = machine.enable

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# Patch machine status by machine_id
@machine.patch("/machines/status/{machine_id}")
def patch_machine_status(machine_id: str, status: bool, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

    # Update the machine status
    machine_model.status = status

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return f"Machine {machine_id} status updated to {status}"


# Patch machine enable by machine_id
@machine.patch("/machines/enable/{machine_id}")
def patch_machine_enable(machine_id: str, enable: bool, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine_model = (
        db.query(Machines).filter(Machines.machine_id == machine_idame).first()
    )

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

    # Update the machine enabled
    machine_model.enable = enable

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    return f"Machine {machine_id} enabled updated to {enable}"


# DELETE

# Delete a machine by machine_id
@machine.delete("/machines/{machine_id}")
def delete_machine(machine_id: str, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

    # Delete the machine from the database
    db.delete(machine_model)
    db.commit()

    # Return the machine deleted
    return machine_model
