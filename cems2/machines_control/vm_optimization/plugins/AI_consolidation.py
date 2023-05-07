"""Generates a consolidation schema to maximize the utilization of the machines."""

from cems2 import log
from cems2.machines_control.vm_optimization.base import VMOptimizationBase

# Get the logger
LOG = log.get_logger(__name__)


class AIConsolidation(VMOptimizationBase):
    """Generates a consolidation schema to maximize the utilization of the machines."""

    def __init__(self):
        """Initialize the consolidation schema."""
        self.consolidation_schema = []
