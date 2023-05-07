"""IPMI Connector plug-in for Power Management."""

from cems2 import log
from cems2.machines_control.pm_connector.base import PMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)


class IPMIPower(PMConnectorBase):
    """Allows to connect to the IPMI interface of the physical machines."""

    def __init__(self):
        """Initialize the connection to the IPMI interface of the physical machines."""
