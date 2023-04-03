# Description: API calls to CRUD operations for the machines table.

from cryptography.fernet import Fernet
from database.config import Base, engine, get_db
from fastapi import APIRouter, Depends, HTTPException
from models.machine import Machines
from schemas.machine import Machine
from sqlalchemy.orm import Session

# Create the machines router
machines = APIRouter()

# Create the databases tables
Base.metadata.create_all(bind=engine)

# Encrypt the passwords using Fernet
key = Fernet.generate_key()
encription = Fernet(key)

# CRUD operations

# CREATE

# Create a new machine
@machines.post("/machines", response_model=Machine)
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
        raise HTTPException(
            status_code=400,
            detail=f"Machine already exists by hostname ({machine.hostname})",
        )

    # Check if the machine already exists (by IP)
    if db.query(Machines).filter(Machines.ip == machine.ip).first():
        raise HTTPException(
            status_code=400,
            detail=f"Machine already exists by IP address ({machine.ip})",
        )

    # Add the machine to the database
    db.add(machine_model)
    db.commit()

    # Return the machine created
    return machine_model


# READ

# Get all the machines
@machines.get("/machines", response_model=list[Machine])
def get_machines(db: Session = Depends(get_db)):

    # Get all the machines from the database
    return db.query(Machines).all()


# Get a machine by machine_id
@machines.get("/machines/{machine_id}")
def get_machine_by_machine_id(machine_id: str, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine is None:
        raise HTTPException(
            status_code=404, detail=f"Machine whit ID: {machine_id} not found"
        )

    # Return the machine
    return machine


# UPDATE

# Update a machine by machine_id
@machines.put("/machines/{machine_id}", response_model=Machine)
def update_machine(machine_id: str, machine: Machine, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=404, detail=f"Machine with ID: {machine_id} not found"
        )

    # Check if the updated data not conflict with other machines (Hostname and IP)
    if db.query(Machines).filter(Machines.hostname == machine.hostname).first():
        raise HTTPException(
            status_code=400,
            detail=f"There is another machine with the same hostname ({machine.hostname})",
        )

    if db.query(Machines).filter(Machines.ip == machine.ip).first():
        raise HTTPException(
            status_code=400,
            detail=f"There is another machine with the same IP address ({machine.ip})",
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
@machines.patch("/machines/status/{machine_id}", response_model=str)
def update_machine_status(machine_id: str, status: bool, db: Session = Depends(get_db)):

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=404, detail=f"Machine with ID: {machine_id} not found"
        )

    # Update the machine status
    machine_model.status = status

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return f"Machine with ID: {machine_id} status updated to {status}"


# Patch machine enable by machine_id
@machines.patch("/machines/enable/{machine_id}", response_model=str)
def update_machine_enable(machine_id: str, enable: bool, db: Session = Depends(get_db)):

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
@machines.delete("/machines/{machine_id}", response_model=Machine)
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
