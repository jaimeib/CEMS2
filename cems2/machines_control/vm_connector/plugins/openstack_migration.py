"""OpenStack VM migration plug-in."""

from cems2 import log
from cems2.machines_control.vm_connector.base import VMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)


class OpenStackMigration(VMConnectorBase):
    """Allows to migrate the virtual machines from the OpenStack cloud platform."""

    def __init__(self):
        """Initialize the connection to the OpenStack cloud platform."""
