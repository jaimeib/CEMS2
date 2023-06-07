"""Generates a list of machines to be turned on or off based on the its utilization."""

import trio

from cems2 import config_loader, log
from cems2.machines_control.pm_optimization.base import PMOptimizationBase

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class TimeUtilization(PMOptimizationBase):
    """Generates a dictionary of machines to be turned on or off based on
    its utilization during a period of time."""

    def __init__(self):
        """Initialize the Time Utilization plugin."""
        self.metrics = None
        self.baseline = None

        # Get the time threshold to be considered
        self.time_threshold = CONFIG.getint(
            "plugins.time_utilization", "time_threshold"
        )

    async def run(self):
        """Run the PMs Optimization."""
        LOG.debug("Running Time Utilization plugin.")

        # Await the baseline to be received
        await self._wait_for_baseline()

        # Await the metrics to be received
        await self._wait_for_metrics()

        # Print the metrics
        print(self.metrics)

    async def _wait_for_baseline(self):
        """Wait for the baseline to be received."""
        if self.baseline is None:
            LOG.debug("Waiting for baseline to be reveived.")
        while self.baseline is None:
            await trio.sleep(1)

    async def _wait_for_metrics(self):
        """Wait for the metrics to be received."""
        if self.metrics is None:
            LOG.debug("Waiting for metrics to be reveived.")
        while self.metrics is None:
            await trio.sleep(1)

    def recieve_metrics(self, metrics):
        """Recieve the metrics from the manager."""
        LOG.debug("Recieving metrics from the manager.")

        # Store the metrics in a proper way
        # Metrics are a dictionary of list of dictionaries of metrics
        # Metrics = {machine_name: [{metric_name: metric_value, ...}, ...], ...}

        for machine_name, metrics_list in metrics.items():
            # Initialize the list of metrics for the machine
            if machine_name not in self.metrics:
                self.metrics[machine_name] = []

            # Add the metrics to the list
            self.metrics[machine_name].extend(metrics_list)

        # Get current time
        current_time = datetime.datetime.now()

        # Get the limit time to be considered for the metrics
        limit_time = current_time - datetime.timedelta(self.time_threshold)

        # For each machine, remove the metrics older than the limit time
        for machine_name, metrics_list in self.metrics.items():
            # Remove the metrics older than the limit time
            self.metrics[machine_name].remove(
                metric for metric in metrics_list if metric["timestamp"] < limit_time
            )

    def recieve_baseline(self, baseline):
        """Recieve the baseline from the manager."""
        LOG.debug("Recieving baseline from the manager.")
        self.baseline = baseline

    async def get_optimization(self):
        """Get the dictionary of machines to be turned on or off.

        :return: Dictionary of machines to be turned on or off.
        :rtype: dict
        """
        LOG.debug("Getting Time Utilization optimization.")
        return self.current_optimization
