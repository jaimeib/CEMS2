"""VMs connector test 2 plug-in."""

from cems2 import log
from cems2.machines_control.vm_connector.base import VMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)


class Test2(VMConnectorBase):
    def __init__(self):
        """Initialize the test connection."""
