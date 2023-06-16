"""API endpoints for the actions controller."""

from fastapi import APIRouter, HTTPException, status

from cems2 import log
from cems2.schemas.machine import Machine
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

    def machines_monitoring(self):
        """
        Get the machines on monitoring state from the Machine Manager.

        :return: List of machines on monitoring state
        :rtype: list[Machine]
        """
        # Create a list to store the machines
        machine_model_list = []
        machine_schema_list = []

        # Get the machines from the Machine Manager (List of Machine models)
        machine_model_list = self.machine_manager.get_machines(monitoring=True)

        # Convert the list of Machine models to a list of Machine schemas
        for machine in machine_model_list:
            machine_schema_list.append(Machine.from_orm(machine))

        # Return the list of machines
        return machine_schema_list

    def machines_available(self):
        """
        Get the machines available from the Machine Manager.

        :return: List of machines available
        :rtype: list[Machine]
        """
        # Create a list to store the machines
        machine_model_list = []
        machine_schema_list = []

        # Get the machines from the Machine Manager (List of Machine models)
        machine_model_list = self.machine_manager.get_machines(available=True)

        # Convert the list of Machine models to a list of Machine schemas
        for machine in machine_model_list:
            machine_schema_list.append(Machine.from_orm(machine))

        # Return the list of machines
        return machine_schema_list

    def notify_update_monitoring(self):
        """Notify the update of the monitoring."""
        self.machines_control_manager.pm_monitoring = self.machines_monitoring()

    def monitor_again(self):
        """Notify the monitoring controller to monitor again."""
        self.monitoring_controller.monitor_again()

    def new_metrics(self, metrics: dict):
        """Get the new metrics from the monitoring controller.

        :param metrics: new metrics
        :type metrics: dict
        """
        self.machines_control_manager.new_metrics(metrics)

    def notify_machine_status(self, machine_list: list[Machine]):
        """Notify the status of a machine to the machine manager.

        :param machine_list: list of machines
        :type machine_list: list[Machine]
        """
        # For each machine in the list
        for machine in machine_list:
            # Update the energy status using the machine manager
            self.machine_manager.update_machine_status_by_hostname(
                machine.hostname, machine.energy_status
            )

        # Notify the monitoring controller about the new status
        self.monitoring_controller.notify_update_monitoring()


# Create the actions controller
actions_controller = ActionsController()


# API ENDPOINTS


@actions.get(
    "/actions/plugins",
    summary="Get the installed plugins by type and status",
    status_code=status.HTTP_200_OK,
    response_model=list[Plugin],
)
def _get_plugins(type: str = None, status: str = None):
    """
    Get the plugins installed by the following types:

    - **vm_optimization**: VMs optimization plugins
    - **pm_optimization**: PMs optimization plugins
    - **vm_connector**: VMs connector plugins
    - **pm_connector**: PMs connector plugins

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

    # Filter the plugins by status
    if status:
        plugin_list = [plugin for plugin in plugin_list if plugin.status == status]

    return plugin_list


@actions.get(
    "/actions/machines_control",
    summary="Get if the machines control system is running",
    status_code=status.HTTP_200_OK,
    response_model=bool,
)
def _get_actions_machines_control():
    """
    Get if the machines control system is running

    **Returns**: A boolean with the state of the machines control system
    """
    return actions_controller.machines_control_manager.running


@actions.put(
    "/actions/machines_control={state}",
    summary="Switch on/off machines control system",
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def _switch_actions_machines_control(state: bool):
    """
    Switch on/off machines control system

    **Returns**: A message with the result of the operation
    """
    # If the state is the same, do nothing
    if actions_controller.machines_control_manager.running == state:
        return Message(
            message="Already {}".format("Running" if state else "Not Running")
        )
    else:
        # If the state is different, switch the state
        actions_controller.machines_control_manager.running = state

        return Message(message="{}".format("Running" if state else "Not Running"))


@actions.get(
    "/actions/vm-optimizations",
    summary="Get the result of the vm optimizations",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, dict],
)
def _get_vm_optimizations(name: str = None):
    """
    Get the last vm optimizations

    **Returns**: A dict with the vm optimizations

    **Raises**: HTTPException (status code 404): VM Optimization not found
    """
    # If a name is provided, check if the vm optimization exists
    if name:
        if (
            name
            not in actions_controller.machines_control_manager.vm_optimization.get_installed_plugins()
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="VM Optimization '{}' not found".format(name),
            )

    return actions_controller.machines_control_manager.get_vm_optimizations(name)


@actions.get(
    "/actions/pm-optimizations",
    summary="Get the result of the pm optimizations",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, dict],
)
def _get_pm_optimizations(name: str = None):
    """
    Get the last pm optimizations

    **Returns**: A dict with the pm optimizations

    **Raises**: HTTPException (status code 404): PM Optimization not found
    """
    # If a name is provided, check if the pm optimization exists
    if name:
        if (
            name
            not in actions_controller.machines_control_manager.pm_optimization.get_installed_plugins()
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PM Optimization '{}' not found".format(name),
            )

    return actions_controller.machines_control_manager.get_pm_optimizations(name)
