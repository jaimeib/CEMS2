"""API endpoints for the actions controller."""

from fastapi import APIRouter, Depends, HTTPException, status

from cems2 import log

# from cems2.__main__ import machines_control_manager
from cems2.schemas.plugin import Plugin

# Create the actions controller router
actions = APIRouter()

# Get the logger
LOG = log.get_logger(__name__)


# API ENDPOINTS
@actions.get(
    "/actions/plugins={plugin_type}",
    summary="Get the installed plugins",
    status_code=status.HTTP_200_OK,
    response_model=list[Plugin],
)
def _get_plugins(plugin_type: str):
    """
    Get the plugins installed by the following types:

    - **vm_optimization**: Virtual Machines optimization plugins
    - **pm_optimization**: Physical Machines optimization plugins
    - **vm_connector**: Virtual Machines connector plugins
    - **pm_connector**: Physical Machines connector plugins

    **Returns**: A list of plugins

    **Raises**: HTTPException (status code 404): No plugins found
    """
    plugin_list = machines_control_manager.get_plugins(plugin_type)

    if not plugin_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plugins found",
        )

    return plugin_list
