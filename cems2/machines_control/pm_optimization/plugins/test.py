"""PMs Optimization test plug-in."""

import json
import random

import trio

from cems2 import log
from cems2.machines_control.pm_optimization.base import PMOptimizationBase

# Get the logger
LOG = log.get_logger(__name__)


class Test(PMOptimizationBase):
    """Allows to test the optimization of the PMs."""

    def __init__(self):
        """Initialize the test connection."""
        self.metrics = None
        self.baseline = None
        self.current_optimization = None

    async def run(self):
        """Run the PMs Optimization."""

        # Run the optimization
        while True:
            # Await the baseline to be recieved
            await self._wait_for_baseline()

            # Await the metrics to be recieved
            await self._wait_for_metrics()

            # Clear the current optimization
            self.current_optimization = None

            # Clear the current distribution
            self.current_distribution = None

            # Compute the distribution
            distribution = self._compute_algorithm()

            # Check the baseline
            optimization = self._check_baseline(distribution)

            # Simulate a delay
            await trio.sleep(random.randint(1, 5))

            # Set the current optimization
            self.current_optimization = optimization

            # Reset the metrics
            self.metrics = None

            # Note: The baseline is not reset, only when the manager updates it

    async def _wait_for_baseline(self):
        """Wait for the baseline to be recieved."""
        if self.baseline is None:
            LOG.debug("Waiting for baseline to be recieved.")
        while self.baseline is None:
            await trio.sleep(1)

    async def _wait_for_metrics(self):
        """Wait for the metrics to be recieved."""
        if self.metrics is None:
            LOG.debug("Waiting for metrics to be recieved.")
        while self.metrics is None:
            await trio.sleep(1)

    def _compute_algorithm(self):
        """Compute the optimization algorithm.

        - If the machine has an utilization metric:
            - If the utilization is greater than 0.0, add the PM to the "on" list
            - If the utilization is 0.0, add the PM to the "off" list

        :return: the distribution
        :rtype: dict
        """
        # Initialize the optimization schema
        distribution = {"on": [], "off": []}

        # For each entry on the metric dictionary
        for key, value in self.metrics.items():
            # Find if there is a "utilization" metric
            for metric in value:
                if metric.name == "utilization":
                    # If the utilization is greater than 0.0
                    if float(json.loads(metric.payload)["value"]) > 0.0:
                        # Add the PM to the "on" list
                        distribution["on"].append(key)
                    else:
                        # Add the PM to the "off" list
                        distribution["off"].append(key)

        # Return the optimization
        return distribution

    def _check_baseline(self, distribution):
        """Check if the result of the optimization is below the baseline.

        :param distribution: the distribution
        :type distribution: dict

        :return: the distribution
        :rtype: dict
        """
        # For the ones that have to be turned off, move to "on", to have a baseline
        for _ in range(self.baseline):
            # If there are machines to be turned off, move them to "on"
            if len(distribution["off"]) > 0:
                # Pick a machine to be turned on randomly
                machine = random.choice(distribution["off"])
                # Remove the machine from the "off" list
                distribution["off"].remove(machine)
                # Add the machine to the "on" list
                distribution["on"].append(machine)
            else:
                break

        return distribution

    def recieve_metrics(self, metrics):
        """Recieve the metrics from the manager.

        :param metrics: the metrics
        :type metrics: dict
        """
        LOG.debug("Metrics recieved in the optimization plugin")
        # Set the metrics
        self.metrics = metrics

    def recieve_baseline(self, baseline):
        """Recieve the baseline from the manager.

        :param baseline: the baseline
        :type baseline: int
        """
        LOG.debug("Baseline recieved in optimization plugin")
        # Set the baseline
        self.baseline = baseline

    async def get_optimization(self):
        """Get the optimization result.

        :return: A dict with the result of the optimization
        :rtype: dict
        """
        if self.current_optimization is None:
            LOG.debug("Waiting for optimization to be calculated.")
        while self.current_optimization is None:
            await trio.sleep(1)

        # Log the optimization
        LOG.debug("Obtained default PM optimization.")

        return self.current_optimization
