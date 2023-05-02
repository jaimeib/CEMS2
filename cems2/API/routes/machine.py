"""API endpoints for the machine manager."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cems2 import log
from cems2.API.database.config import get_db
from cems2.API.models.machine import Machines
from cems2.API.routes import actions as actions_controller
from cems2.API.routes import monitoring as monitoring_controller
from cems2.schemas.machine import Machine
from cems2.schemas.message import Message

# Create the machines manager router
machines = APIRouter()

# Get the LOG
LOG = log.get_logger(__name__)

# CRUD operations (Only read and update status and monitoring)
# The rest of the operations and modifications are done through the configuration files

# API ENDPOINTS


@machines.get(
    "/machines",
    response_model=list[Machine],
    status_code=status.HTTP_200_OK,
    summary="Get all the machines",
)
def _get_machines(
    group_name: str = None,
    brand_model: str = None,
    energy_status: bool = None,
    monitoring: bool = None,
    available: bool = None,
    db_session: Session = Depends(get_db),
):
    """Get all the machines from the database with the following data:

    - **id**: The ID of the machine
    - **groupname**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **brand_name**: The comercial name of the machine
    - **management_ip**: The IP address to manage the machine (unique)
    - **management_username**: The username to manage the machine
    - **management_password**: The password to manage the machine
    - **energy_status**: True if the machine is on, False otherwise
    - **monitoring**: True if the machine is being monitored, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    - **created_at**: The date and time when the machine was created
    - **updated_at**: The date and time when the machine was updated

    **Returns:** The machines

    **Optional filters:** The machines can be filtered by the following parameters:
    - **group_name**: The group name of the machine
    - **brand_model**: The brand model of the machine
    - **energy_status**: True if the machine is on, False otherwise
    - **monitoring**: True if the machine is being monitored, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    """
    # Get the machines from the database
    machines_model = db_session.query(Machines).all()

    # Filter by group
    if group_name is not None:
        machines_model = [
            machine for machine in machines_model if machine.groupname == group_name
        ]

    # Filter by brand_model
    if brand_model is not None:
        machines_model = [
            machine for machine in machines_model if machine.brand_model == brand_model
        ]

    if energy_status is not None:
        machines_model = [
            machine
            for machine in machines_model
            if machine.energy_status == energy_status
        ]

    if monitoring is not None:
        machines_model = [
            machine for machine in machines_model if machine.monitoring == monitoring
        ]

    if available is not None:
        machines_model = [
            machine for machine in machines_model if machine.available == available
        ]

    # Return the machines
    return machines_model


@machines.get(
    "/machines/id={id}",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Get a machine by its ID",
    responses={404: {"description": "Machine not found by ID", "model": Message}},
)
def _get_machine_by_id(id: int, db_session: Session = Depends(get_db)):
    """Get a machine from the database by its ID with the following data:

    - **id**: The ID of the machine
    - **groupname**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **username**: The username to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    - **created_at**: The date and time when the machine was created
    - **updated_at**: The date and time when the machine was updated

    **Raises:**
    - **HTTPException: 404**: If the machine does not exist by ID

    **Returns:** The machine
    """
    # Get the machine from the database
    machine_model = db_session.query(Machines).filter(Machines.id == id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {id} not found",
        )

    # Return the machine
    return machine_model


@machines.get(
    "/machines/hostname={hostname}",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Get a machine by its hostname",
    responses={404: {"description": "Machine not found by hostname", "model": Message}},
)
def _get_machine_by_hostname(hostname: str, db_session: Session = Depends(get_db)):
    """Get a machine from the database by its hostname with the following data:

    - **id**: The ID of the machine
    - **groupname**: The group name of the machine
    - **hostname**: The hostname of the machine (unique)
    - **model**: The comercial name of the machine
    - **ip**: The IP address to manage the machine (unique)
    - **username**: The username to manage the machine
    - **password**: The password to manage the machine
    - **status**: True if the machine is on, False otherwise
    - **available**: True if the machine is availabled on the system, False otherwise
    - **created_at**: The date and time when the machine was created
    - **updated_at**: The date and time when the machine was updated

    **Raises:**
    - **HTTPException: 404**: If the machine does not exist by hostname

    **Returns:** The machine
    """
    # Get the machine from the database
    machine_model = (
        db_session.query(Machines).filter(Machines.hostname == hostname).first()
    )

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Return the machine
    return machine_model


@machines.patch(
    "/machines/id={id}/status",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update a machine energy status by its ID",
    responses={
        404: {"description": "Machine not found by ID", "model": Message},
        400: {
            "description": "Machine is not available or not being monitored",
            "model": Message,
        },
    },
)
def _update_machine_status(
    id: str, energy_status: bool, db_session: Session = Depends(get_db)
):
    """Update a machine energy status by its ID.

    **Raises:**
    - **HTTPException: 404**: If the machine does not exist by its ID
    - **HTTPException: 400**: If the machine is not available or not being monitored

    **Returns:** The updated machine
    """
    # Get the machine from the database
    machine_model = db_session.query(Machines).filter(Machines.id == id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {id} not found",
        )

    # Check if there is not change in the energy status
    if machine_model.energy_status == energy_status:
        return machine_model

    # Check if the machine is available and being monitored to update the energy status
    if machine_model.available and machine_model.monitoring:
        machine_model.energy_status = energy_status
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID: {id} not updated: is not available or not being monitored",
        )

    # Update the machine in the database
    db_session.add(machine_model)
    db_session.commit()

    # Log the machine status update
    LOG.critical(f"Machine with ID: {id} updated: energy status is {energy_status}")

    # Return the machine updated
    return machine_model


@machines.patch(
    "/machines/hostname={hostname}/status",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update a machine energy status by its hostname",
    responses={
        404: {"description": "Machine not found by hostname", "model": Message},
        400: {
            "description": "Machine is not available or not being monitored",
            "model": Message,
        },
    },
)
def _update_machine_status_by_hostname(
    hostname: str, energy_status: bool, db_session: Session = Depends(get_db)
):
    """Update a machine energy status by its hostname.

    **Raises:**
    - HTTPException: 404 - If the machine does not exist by hostname
    - HTTPException: 400 - If the machine is not available or not being monitored

    **Returns:** The updated machine
    """
    # Get the machine from the database
    machine_model = (
        db_session.query(Machines).filter(Machines.hostname == hostname).first()
    )

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Check if there is not change in the energy status
    if machine_model.energy_status == energy_status:
        return machine_model

    # Check if the machine is available and being monitored to update the status
    if machine_model.available and machine_model.monitoring:
        machine_model.energy_status = energy_status
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID: {hostname} not updated: is not available or not being monitored",
        )

    # Update the machine in the database
    db_session.add(machine_model)
    db_session.commit()

    # Log the machine status
    LOG.critical(
        f"Machine with hostname: {hostname} updated: energy status to {energy_status}"
    )

    # Return the machine updated
    return machine_model


@machines.patch(
    "/machines/id={id}/monitoring",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update if the machine has to be monitored by its ID",
    responses={
        404: {"description": "Machine not found by its ID", "model": Message},
        400: {
            "description": "Machine is not available",
            "model": Message,
        },
    },
)
def _update_machine_monitoring(
    id: str, monitoring: bool, db_session: Session = Depends(get_db)
):
    """Update if the machine has to be monitored or not in the system by its ID.

    **Raises:**
    - **HTTPException: 404**: - If the machine does not exist by its ID
    - **HTTPException: 400**: - If the machine is not available

    **Returns:** The updated machine
    """
    # Get the machine from the database
    machine_model = db_session.query(Machines).filter(Machines.id == id).first()

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID: {id} not found",
        )

    # Check if the machine is not being updated
    if machine_model.monitoring == monitoring:
        return machine_model

    # Check if the machine is available to update the monitoring
    if machine_model.available:
        machine_model.monitoring = monitoring
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID: {id} not updated: is not available ",
        )

    # Update the machine in the database
    db_session.add(machine_model)
    db_session.commit()

    # Log the machine monitoring update
    LOG.warning(f"Machine with ID: {id} monitoring updated to: {monitoring}")

    # Notify the machine monitoring update to the monitoring controller
    monitoring_controller.notify_update_monitoring()

    # Return the machine updated
    return machine_model


@machines.patch(
    "/machines/hostname={hostname}/monitoring",
    response_model=Machine,
    status_code=status.HTTP_200_OK,
    summary="Update if the machines has to be monitored by hostname",
    responses={
        404: {"description": "Machine not found by hostname", "model": Message},
        400: {
            "description": "Machine is not available",
            "model": Message,
        },
    },
)
def _update_machine_monitoring_by_hostname(
    hostname: str, monitoring: bool, db_session: Session = Depends(get_db)
):
    """Update if the machine has to be monitored or not in the system by its hostname.

    **Raises:**
    - **HTTPException: 404**: - If the machine does not exist by hostname
    - **HTTPException: 400**: - If the machine is not available

    **Returns:** The updated machine
    """
    # Get the machine from the database
    machine_model = (
        db_session.query(Machines).filter(Machines.hostname == hostname).first()
    )

    # Check if the machine exists
    if machine_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with hostname: {hostname} not found",
        )

    # Check if the machine is not being updated
    if machine_model.monitoring == monitoring:
        return machine_model

    # Check if the machine is available to update the monitoring
    if machine_model.available:
        machine_model.monitoring = monitoring
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID: {id} not updated: is not available",
        )

    # Update the machine in the database
    db_session.add(machine_model)
    db_session.commit()

    # Log the machine monitoring update
    LOG.warning(
        f"Machine with hostname: {hostname} monitoring updated to: {monitoring}"
    )

    # Notify the machine monitoring update to the monitoring controller
    monitoring_controller.notify_update_monitoring()

    # Return the machine updated
    return machine_model


# INTERNAL METHODS
def get_machines(
    group_name: str = None,
    brand_model: str = None,
    energy_status: bool = None,
    monitoring: bool = None,
    available: bool = None,
):
    """Get the machines from the database.

    :param group_name: The group name of the machines
    :type group_name: str

    :param brand_model: The brand model of the machines
    :type brand_model: str

    :param energy_status: The energy status of the machines
    :type energy_status: bool

    :param monitoring: The monitoring status of the machines
    :type monitoring: bool

    :param available: The availability status of the machines
    :type available: bool

    :return: The machines
    :rtype: list[Machine (Model)]
    """
    try:
        machine_list = _get_machines(
            group_name=group_name,
            brand_model=brand_model,
            energy_status=energy_status,
            monitoring=monitoring,
            available=available,
            db_session=next(get_db()),
        )
    except Exception as e:
        LOG.error(f"Error getting the machines: {e}")
        exit(1)

    return machine_list
