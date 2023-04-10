# Description: API calls to CRUD operations for the machines table.

from cryptography.fernet import Fernet
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.machine import Machines
from schemas.machine import BaseMachine, Machine
from sqlalchemy.orm import Session

# Create the machines router
machines = APIRouter()

# Encrypt the passwords using Fernet
key = Fernet.generate_key()
encription = Fernet(key)

# CRUD operations

# CREATE


# Create a new machine
@machines.post(
    "/machines",
    response_model=Machine,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new machine",
    deprecated=True,
)
def create_machine(machine: BaseMachine, db: Session = Depends(get_db)):
    """
    Create a new machine with the following data:

    - **group_name**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **user**: The user to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise

    **Raises:**
        HTTPException: 404 - If the machine already exists by hostname or IP address

    **Returns:**
        The machine created
    """

    # Create a new machine model with the data from the request
    machine_model = Machines()

    # Copy the data from the request to the model
    for key, value in machine.dict().items():
        setattr(machine_model, key, value)

    # Encrypt the password before saving it to the database
    machine_model.password = encription.encrypt(machine.password.encode())

    # Check if the machine already exists (by hostname)
    if db.query(Machines).filter(Machines.hostname == machine.hostname).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine already exists by hostname ({machine.hostname})",
        )

    # Check if the machine already exists (by IP)
    if db.query(Machines).filter(Machines.ip == machine.ip).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine already exists by IP address ({machine.ip})",
        )

    # Add the machine to the database
    db.add(machine_model)
    db.commit()

    # Return the machine created
    return machine_model


# READ


# Get all the machines (with optional filter by group)
@machines.get(
    "/machines",
    response_model=list[Machine],
    status_code=status.HTTP_200_OK,
    summary="Get all the machines",
)
def get_machines(group: str = None, db: Session = Depends(get_db)):
    """
    Get all the machines from the database with the following data:

    - **machine_id**: The ID of the machine
    - **group_name**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **user**: The user to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    - **created_at**: The date and time when the machine was created
    - **updated_at**: The date and time when the machine was updated

    **Returns:** The machines
    """

    # Get the machines from the database
    if group is None:
        machines_model = db.query(Machines).all()
    else:
        # Check if the group exists
        if db.query(Machines).filter(Machines.group_name == group).first():
            machines_model = (
                db.query(Machines).filter(Machines.group_name == group).all()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group ({group}) does not exist",
            )

    # Return the machines
    return machines_model


# Get a machine by its ID (machine_id)
@machines.get(
    "/machines/id={machine_id}",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Get a machine by its ID",
)
def get_machine_by_id(machine_id: int, db: Session = Depends(get_db)):
    """
    Get a machine from the database by its ID with the following data:

    - **machine_id**: The ID of the machine
    - **group_name**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **user**: The user to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    - **created_at**: The date and time when the machine was created
    - **updated_at**: The date and time when the machine was updated

    **Raises:** HTTPException: 404 - If the machine does not exist by ID

    **Returns:** The machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {machine_id} not found",
        )

    # Return the machine
    return machine_model


# Get a machine by hostname
@machines.get(
    "/machines/hostname={hostname}",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Get a machine by its hostname",
)
def get_machine_by_hostname(hostname: str, db: Session = Depends(get_db)):
    """
    Get a machine from the database by its hostname with the following data:

    - **machine_id**: The ID of the machine
    - **group_name**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **user**: The user to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    - **created_at**: The date and time when the machine was created
    - **updated_at**: The date and time when the machine was updated

    **Raises:** HTTPException: 404 - If the machine does not exist by hostname

    **Returns:** The machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.hostname == hostname).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Return the machine
    return machine_model


# UPDATE


# Update a machine by machine_id
@machines.put(
    "/machines/id={machine_id}",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update a machine by its ID",
)
def update_machine_by_id(
    machine_id: str, machine: BaseMachine, db: Session = Depends(get_db)
):
    """
    Update a machine from the database by its ID with the following data:

    - **group_name**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **user**: The user to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is available on the system, False otherwise

    **Raises:**
        HTTPException: 404 - If the machine does not exist by ID or if the updated data not conflict with other machines (Hostname and IP)

    **Returns:** The updated machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {machine_id} not found",
        )

    # Check if the updated data not conflict with other machines (Hostname and IP)
    if db.query(Machines).filter(Machines.hostname == machine.hostname).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is another machine with the same hostname ({machine.hostname})",
        )

    if db.query(Machines).filter(Machines.ip == machine.ip).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is another machine with the same IP address ({machine.ip})",
        )

    # Copy the data from the request to the model
    for key, value in machine.dict().items():
        setattr(machine_model, key, value)

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# Update a machine by hostname
@machines.put(
    "/machines/hostname={hostname}",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update a machine by its hostname",
)
def update_machine_by_hostname(
    hostname: str, machine: BaseMachine, db: Session = Depends(get_db)
):
    """
    Update a machine from the database by its hostname with the following data:

    - **group_name**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **user**: The user to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise

    **Raises:**
        HTTPException: 404 - If the machine does not exist by hostname or if the updated data not conflict with other machines (Hostname and IP)

    **Returns:** The updated machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.hostname == hostname).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Check if the updated data not conflict with other machines (Hostname and IP)
    if db.query(Machines).filter(Machines.hostname == machine.hostname).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is another machine with the same hostname ({machine.hostname})",
        )

    if db.query(Machines).filter(Machines.ip == machine.ip).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is another machine with the same IP address ({machine.ip})",
        )

    # Copy the data from the request to the model
    for key, value in machine.dict().items():
        setattr(machine_model, key, value)

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# Patch machine status by machine_id
@machines.patch(
    "/machines/id={machine_id}/status",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update a machine status by its ID",
)
def update_machine_status(machine_id: str, status: bool, db: Session = Depends(get_db)):
    """
    Update a machine status by its ID

    **Raises:** HTTPException: 404 - If the machine does not exist by ID

    **Returns:** The updated machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {machine_id} not found",
        )

    # Update the machine status
    machine_model.status = status

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# Patch machine status by hostname
@machines.patch(
    "/machines/hostname={hostname}/status",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update a machine status by its hostname",
)
def update_machine_status_by_hostname(
    hostname: str, status: bool, db: Session = Depends(get_db)
):
    """
    Update a machine status by its hostname

    **Raises:** HTTPException: 404 - If the machine does not exist by hostname

    **Returns:** The updated machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.hostname == hostname).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Update the machine status
    machine_model.status = status

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# Patch machine availability by machine_id
@machines.patch(
    "/machines/id={machine_id}/available",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update the availability by its ID",
)
def update_machine_available(
    machine_id: str, available: bool, db: Session = Depends(get_db)
):
    """
    Update if the machine is available or not in the system by its ID

    **Raises:** HTTPException: 404 - If the machine does not exist by ID

    **Returns:** The updated machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {machine_id} not found",
        )

    # Update the machine availabled
    machine_model.available = available

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# Patch machine availability by hostname
@machines.patch(
    "/machines/hostname={hostname}/available",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update the availability by its hostname",
)
def update_machine_available_by_hostname(
    hostname: str, available: bool, db: Session = Depends(get_db)
):
    """
    Update if the machine is available or not in the system by its hostname

    **Raises:** HTTPException: 404 - If the machine does not exist by hostname

    **Returns:** The updated machine
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.hostname == hostname).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Update the machine availabled
    machine_model.available = available

    # Update the machine in the database
    db.add(machine_model)
    db.commit()

    # Return the machine updated
    return machine_model


# DELETE


# Delete a machine by machine_id
@machines.delete(
    "/machines/id={machine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a machine by its ID",
)
def delete_machine(machine_id: str, db: Session = Depends(get_db)):
    """
    Delete a machine from the database by its ID

    **Raises:** HTTPException: 404 - If the machine does not exist by ID

    **Returns:** Status code: 204 - No Content
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.machine_id == machine_id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {machine_id} not found",
        )

    # Delete the machine from the database
    db.delete(machine_model)
    db.commit()

    # Return the machine deleted
    return status.HTTP_204_NO_CONTENT


# Delete a machine by hostname
@machines.delete(
    "/machines/hostname={hostname}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a machine by its hostname",
)
def delete_machine(hostname: str, db: Session = Depends(get_db)):
    """
    Delete a machine from the database by its hostname

    **Raises:** HTTPException: 404 - If the machine does not exist by hostname

    **Returns:** Status code: 204 - No Content
    """

    # Get the machine from the database
    machine_model = db.query(Machines).filter(Machines.hostname == hostname).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Delete the machine from the database
    db.delete(machine_model)
    db.commit()

    # Return the machine deleted
    return status.HTTP_204_NO_CONTENT
