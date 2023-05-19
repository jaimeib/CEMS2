"""API endpoints for the actions controller."""

from fastapi import APIRouter, Depends, HTTPException, status

from cems2 import log
from cems2.API.routes import machine as machine_manager
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

    def set_machines_control_manager(self, machines_control_manager):
        """Set the machines control manager.

        :param machines_control_manager: machines control manager
        :type machines_control_manager: Manager
        """
        self.machines_control_manager = machines_control_manager


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


# INTERNAL METHODS
