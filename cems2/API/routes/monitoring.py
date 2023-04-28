"""
API endpoints for the monitoring controller
"""

from fastapi import APIRouter, Depends, HTTPException, status

from cems2 import log
from cems2.schemas.message import Message
from cems2.schemas.metric import Metric

API_URI = "http://localhost:8000"

# Create the monitoring controller router
monitoring = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)

# Metrics API calls


# Get the lastest metrics from the cloud analytics application
@monitoring.get(
    "/metrics",
    summary="Get the lastest metrics from the cloud analytics application",
    status_code=status.HTTP_200_OK,
    response_model=list[Metric],
)
def get_metrics(metric_name: str = None):
    """
    Get the lastest metrics from the cloud analytics application with the following data:

    - **name**: Name of the metric
    - **value**: Value of the metric
    - **unit**: Unit of the metric
    - **timestamp**: Timestamp of the metric
    - **hostname**: Hostname of the machine

    **Returns**: A list of metrics

    **Optional filters:** The metrics can be filtered by the following parameters:
    - **metric_name**: Name of the metric
    """

    # Obtain the metrics from the Cloud Analytics Application
    metric_list = []

    return metric_list


# Get the lastest metrics from the cloud analytics application by the machine id
@monitoring.get(
    "/metrics/id={id}",
    summary="Get the lastest metrics from the cloud analytics application of a machine by its id",
    status_code=status.HTTP_200_OK,
    response_model=list[Metric],
)
def get_metrics_by_id(id: str, metric_name: str = None):
    """
    Get the lastest metrics from the cloud analytics application of a machine by its id with the following data:

    - **name**: Name of the metric
    - **value**: Value of the metric
    - **unit**: Unit of the metric
    - **timestamp**: Timestamp of the metric
    - **hostname**: Hostname of the machine

    **Returns**: A list of metrics

    **Optional filters:** The metrics can be filtered by the following parameters:
    - **metric_name**: Name of the metric
    """

    # Create a list to store the metrics
    metric_list = []

    # Return the list of metrics
    return metric_list


# Get the lastest metrics from the cloud analytics application by the machine hostname
@monitoring.get(
    "/metrics/hostname={hostname}",
    summary="Get the lastest metrics from the cloud analytics application by the machine hostname",
    status_code=status.HTTP_200_OK,
    response_model=list[Metric],
)
def get_metrics_by_hostname(hostname: str, metric_name: str = None):
    """
    Get the lastest metrics from the cloud analytics application by the machine hostname with the following data:

    - **name**: Name of the metric
    - **value**: Value of the metric
    - **unit**: Unit of the metric
    - **timestamp**: Timestamp of the metric
    - **hostname**: Hostname of the machine

    **Returns**: A list of metrics

    **Optional filters:** The metrics can be filtered by the following parameters:
    - **metric_name**: Name of the metric
    """

    # Obtain the metrics from the Cloud Analytics Application
    metric_list = []

    # Return the list of metrics
    return metric_list


# TODO: Estado energetico se obtiene a traves de OpenStack o IPMI?

# Internal functions to communicate with the Cloud Analytics Application


# Get the machines on monitoring state
def machines_on_monitoring():
    """
    Get the machines on monitoring state from the Cloud Analytics Application

    **Returns**: A list of machines
    """

    # Obtain the machines on monitoring state from the Cloud Analytics Application
    machine_list = []

    return machine_list
