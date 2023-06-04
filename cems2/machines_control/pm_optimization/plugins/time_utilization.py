"""Generates a list of machines to be turned on or off based on the its utilization."""

from cems2 import log
from cems2.machines_control.pm_optimization.base import PMOptimizationBase

# Get the logger
LOG = log.get_logger(__name__)


class TimeUtilization(PMOptimizationBase):
    """Generates a list of machines to be turned on or off based on
    its utilization during a period of time."""

    def __init__(self):
        """Initialize the list of machines to be turned on or off."""

    async def run(self):
        """Run the Physical Machines Optimization."""
        LOG.debug("Running Time Utilization plugin.")
