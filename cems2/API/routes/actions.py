"""API endpoints for the actions controller."""

from fastapi import APIRouter, Depends, HTTPException, status

from cems2 import log
from cems2.schemas.message import Message
from cems2.schemas.plugin import Plugin

# Create the actions controller router
actions = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)


class ActionsController(object):
    """Actions Controller class."""

    def __init__(self):
        """Initialize the controller."""
        self.machines_control_manager = None
        self.machine_manager = None
        self.monitoring_controller = None

    def set_machines_control_manager(self, machines_control_manager):
        """Set the machines control manager.

        :param machines_control_manager: machines control manager
        :type machines_control_manager: Manager
        """
        self.machines_control_manager = machines_control_manager

    def set_machine_manager(self, machine_manager):
        """Set the machine manager.

        :param machine_manager: machine manager
        :type machine_manager: MachineManager
        """
        self.machine_manager = machine_manager

    def set_monitoring_controller(self, monitoring_controller):
        """Set the monitoring controller.

        :param monitoring_controller: monitoring controller
        :type monitoring_controller: MonitoringController
        """
        self.monitoring_controller = monitoring_controller

    def notify_update_monitoring(self):
        """Notify the update of the monitoring."""
        self.machine_manager.physical_machines = (
            self.monitoring_controller.get_machines_on_monitoring()
        )

    def new_metrics(self, metrics: dict):
        """Get the new metrics from the monitoring controller.

        :param metrics: new metrics
        :type metrics: dict
        """
        self.machines_control_manager.new_metrics(metrics)


# Create the actions controller
actions_controller = ActionsController()


# API ENDPOINTS


@actions.get(
    "/actions/plugins",
    summary="Get the installed plugins by type",
    status_code=status.HTTP_200_OK,
    response_model=list[Plugin],
)
def _get_plugins(type: str = None):
    """
    Get the plugins installed by the following types:

    - **vm_optimization**: Virtual Machines optimization plugins
    - **pm_optimization**: Physical Machines optimization plugins
    - **vm_connector**: Virtual Machines connector plugins
    - **pm_connector**: Physical Machines connector plugins

    **Returns**: A list of plugins

    **Raises**: HTTPException (status code 404): No plugins found
    """
    plugin_list = actions_controller.machines_control_manager.get_plugins()

    if not plugin_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plugins found",
        )

    # Filter the plugins by type
    if type:
        plugin_list = [plugin for plugin in plugin_list if plugin.type == type]

    return plugin_list


@actions.get(
    "/actions/machines_control",
    summary="Get if the machines control application is running",
    status_code=status.HTTP_200_OK,
    response_model=bool,
)
def _get_actions_machines_control():
    """
    Get if the machines control application is running

    **Returns**: A boolean with the state of the machines control application
    """
    return actions_controller.machines_control_manager.running


# Switch on/off actions
@actions.put(
    "/actions/machines_control={state}",
    summary="Switch on/off machines control actions",
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def _switch_actions_machines_control(state: bool):
    """
    Switch on/off machines control actions

    **Returns**: A message with the result of the operation
    """
    # If the state is the same, do nothing
    if actions_controller.machines_control_manager.running == state:
        return Message(
            message="Machines Control Application already {}".format(
                "on" if state else "off"
            )
        )
    else:
        # If the state is different, switch the state
        actions_controller.machines_control_manager.running = state

        return Message(
            message="Machines Control Application {}".format("on" if state else "off")
        )
