"""Generates a list of machines to be turned on or off based on the its utilization."""

from cems2 import log
from cems2.machines_control.pm_connector.base import PMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)


class AIPower(PMConnectorBase):
    """Generates a list of machines to be turned on or off based on the its utilization."""

    def __init__(self):
        """Initialize the list of machines to be turned on or off."""

    def optimize(self, pm_list):
        """Optimize the physical machines.

        :param pm_list: list of physical machines
        :type pm_list: list

        """
        LOG.info("Optimizing the physical machines")
