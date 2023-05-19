"""API endpoints for the monitoring controller."""

from fastapi import APIRouter, HTTPException, status

from cems2 import log
from cems2.API.routes import machine as machine_manager
from cems2.schemas.machine import Machine
from cems2.schemas.message import Message
from cems2.schemas.metric import Metric
from cems2.schemas.plugin import Plugin

# Create the monitoring controller router
monitoring = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)


class MonitoringController(object):
    """Monitoring Controller class."""

    def __init__(self):
        """Initialize the controller."""
        self.cloud_analytics_manager = None

    def set_cloud_analytics_manager(self, cloud_analytics_manager):
        """Set the cloud analytics manager.

        :param cloud_analytics_manager: cloud analytics manager
        :type cloud_analytics_manager: Manager
        """
        self.cloud_analytics_manager = cloud_analytics_manager


# Create the monitoring controller
monitoring_controller = MonitoringController()


# API ENDPOINTS


@monitoring.get(
    "/monitoring/metrics",
    summary="Get the lastest metrics from the cloud analytics application",
    status_code=status.HTTP_200_OK,
    response_model=list[Metric],
)
def _get_metrics(metric_name: str = None):
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


@monitoring.get(
    "/monitoring/metrics/id={id}",
    summary="Get the lastest metrics from the cloud analytics application of a machine by its id",
    status_code=status.HTTP_200_OK,
    response_model=list[Metric],
)
def _get_metrics_by_id(id: str, metric_name: str = None):
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


@monitoring.get(
    "/monitoring/metrics/hostname={hostname}",
    summary="Get the lastest metrics from the cloud analytics application by the machine hostname",
    status_code=status.HTTP_200_OK,
    response_model=list[Metric],
)
def _get_metrics_by_hostname(hostname: str, metric_name: str = None):
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


@monitoring.get(
    "/monitoring/plugins",
    summary="Get the plugins installed by type (Collector or Reporter)",
    status_code=status.HTTP_200_OK,
    response_model=list[Plugin],
)
def _get_plugins(type: str = None):
    """
    Get the plugins installed by type (Collector or Reporter).

    **Returns**: A list of plugins

    **Raises**: HTTPException (status code 404): No plugins found
    """
    plugin_list = monitoring_controller.cloud_analytics_manager.get_plugins()

    if not plugin_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plugins found",
        )

    # Filter the plugins by type
    if type:
        plugin_list = [plugin for plugin in plugin_list if plugin.type == type]

    return plugin_list


# INTERNAL METHODS


def machines_on_monitoring():
    """
    Get the machines on monitoring state from the Cloud Analytics Application.

    :return: List of machines on monitoring state
    :rtype: list[Machine]
    """
    # Create a list to store the machines
    machine_model_list = []
    machine_schema_list = []

    # Get the machines from the Machine Manager (List of Machine models)
    machine_model_list = machine_manager.get_machines(monitoring=True)

    # Convert the list of Machine models to a list of Machine schemas
    for machine in machine_model_list:
        machine_schema_list.append(Machine.from_orm(machine))

    # Return the list of machines
    return machine_schema_list


def notify_update_monitoring():
    """Notify to the CloudAnalyticsManager a machine update."""
    monitoring_controller.cloud_analytics_manager.machines_monitoring = (
        machines_on_monitoring()
    )
