"""VM optimization test plug-in."""

import random

import trio

from cems2 import log
from cems2.machines_control.vm_optimization.base import VMOptimizationBase

# Get the logger
LOG = log.get_logger(__name__)


class Test(VMOptimizationBase):
    def __init__(self):
        """Initialize the test connection."""
        self.metrics = None
        self.current_optimization = None
