"""API endpoints for the monitoring controller."""

from fastapi import APIRouter, HTTPException, status

from cems2 import log
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
        self.machine_manager = None
        self.actions_controller = None

    def set_cloud_analytics_manager(self, cloud_analytics_manager):
        """Set the cloud analytics manager.

        :param cloud_analytics_manager: cloud analytics manager
        :type cloud_analytics_manager: Manager
        """
        self.cloud_analytics_manager = cloud_analytics_manager

    def set_machine_manager(self, machine_manager):
        """Set the machine manager.

        :param machine_manager: machine manager
        :type machine_manager: Manager
        """
        self.machine_manager = machine_manager

    def set_actions_controller(self, actions_controller):
        """Set the actions controller.

        :param actions_controller: actions controller
        :type actions_controller: ActionsController
        """
        self.actions_controller = actions_controller

    def machines_monitoring_and_on(self):
        """
        Get the machines on monitoring state and power on from the Machine Manager.

        :return: List of machines on monitoring state and energy status on
        :rtype: list[Machine]
        """
        # Create a list to store the machines
        machine_model_list = []
        machine_schema_list = []

        # Get the machines from the Machine Manager (List of Machine models)
        machine_model_list = self.machine_manager.get_machines(
            monitoring=True, energy_status=True
        )

        # Convert the list of Machine models to a list of Machine schemas
        for machine in machine_model_list:
            machine_schema_list.append(Machine.from_orm(machine))

        # Return the list of machines
        return machine_schema_list

    def notify_update_monitoring(self):
        """Notify to the CloudAnalyticsManager a machine update."""
        self.cloud_analytics_manager.machines_monitoring = (
            self.machines_monitoring_and_on()
        )

    def monitor_again(self):
        """Notify to the CloudAnalyticsManager to monitor again."""
        self.cloud_analytics_manager.monitor_again()

    def notify_new_metrics(self, metrics: dict):
        """Notify to the ActionsController a new metrics update."""
        self.actions_controller.new_metrics(metrics)


# Create the monitoring controller
monitoring_controller = MonitoringController()


# API ENDPOINTS


@monitoring.get(
    "/monitoring/metrics",
    summary="Get the lastest metrics from the cloud analytics application",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, list[Metric]],
)
def _get_metrics(metric_name: str = None):
    """
    Get the lastest metrics from the cloud analytics application with the following data:

    - **name**: Name of the metric
    - **value**: Value of the metric
    - **unit**: Unit of the metric
    - **timestamp**: Timestamp of the metric
    - **hostname**: Hostname of the machine

    **Returns**: A dict of metrics

    **Optional filters:** The metrics can be filtered by the following parameters:
    - **metric_name**: Name of the metric
    """
    # Obtain the metrics from the Cloud Analytics Application
    metric_dict = monitoring_controller.cloud_analytics_manager.obtain_last_metrics()

    # Filter the metrics by metric_name
    if metric_name:
        # For each machine in the dict of metrics (key: hostname, value: list of metrics)
        for machine in metric_dict:
            # Filter the metrics by metric_name
            metric_dict[machine] = [
                metric for metric in metric_dict[machine] if metric.name == metric_name
            ]

    # Return the dict of metrics
    return metric_dict


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

    **Raises:**
    - **HTTPException: 404**: If the machine does not exist by its ID
    - **HTTPException: 400**: If the machine is not being monitored
    """

    # Check if the machine exists and raise an exception if it does not
    machine = monitoring_controller.machine_manager.get_machine_by_id(id)

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID: {id} does not exist",
        )

    # Check if the machine is on monitoring state and raise an exception if it is not
    if not machine.monitoring:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with ID: {id} is not on monitoring state",
        )

    # Call the generic function _get_metrics and then filter by id
    metric_dict = _get_metrics(metric_name)

    # If the machine is not in the dict of metrics, return an empty list
    if machine.hostname not in metric_dict:
        return []
    else:
        return metric_dict[machine.hostname]


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

    **Raises:**
    - **HTTPException: 404**: If the machine does not exist by its hostname
    - **HTTPException: 400**: If the machine is not being monitored
    """

    # Check if the machine exists and raise an exception if it does not
    machine = monitoring_controller.machine_manager.get_machine_by_hostname(hostname)

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with hostname: {hostname} does not exist",
        )

    # Check if the machine is on monitoring state and raise an exception if it is not
    if not machine.monitoring:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Machine with hostname: {hostname} is not on monitoring state",
        )

    # Call the generic function _get_metrics and then filter by hostname
    metric_dict = _get_metrics(metric_name)

    # If the machine is not in the dict of metrics, return an empty list
    if machine.hostname not in metric_dict:
        return []
    else:
        return metric_dict[machine.hostname]


@monitoring.get(
    "/monitoring/plugins",
    summary="Get the plugins installed by type (Collector or Reporter)",
    status_code=status.HTTP_200_OK,
    response_model=list[Plugin],
)
def _get_plugins(type: str = None):
    """
    Get the plugins installed by type.

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


# Get if the cloud analytics application is running
@monitoring.get(
    "/monitoring/cloud-analytics",
    summary="Get if the cloud analytics application is running",
    status_code=status.HTTP_200_OK,
    response_model=bool,
)
def _get_monitoring_cloud_analytics():
    """
    Get if the cloud analytics application is running.

    **Returns**: A boolean with the state of the cloud analytics application
    """
    return monitoring_controller.cloud_analytics_manager.running


@monitoring.put(
    "/monitoring/cloud-analytics={state}",
    summary="Switch on/off monitoring of the cloud analytics application",
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def _switch_monitoring_cloud_analytics(state: bool):
    """
    Switch on/off monitoring of the cloud analytics application.

    **Returns**: A message with the result of the operation
    """
    # If the state is the same, do nothing
    if monitoring_controller.cloud_analytics_manager.running == state:
        return Message(
            message="Cloud Analytics Application is already {}".format(
                "on" if state else "off"
            )
        )
    else:
        # If the state is different, switch the state
        monitoring_controller.cloud_analytics_manager.running = state

        return Message(
            message="Cloud Analytics Application switched {}".format(
                "on" if state else "off"
            )
        )
