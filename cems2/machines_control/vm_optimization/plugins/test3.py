"""VM optimization test 3 plug-in."""

import copy
import json
import random

import rich
import trio

from cems2 import log
from cems2.machines_control.vm_optimization.base import VMOptimizationBase

# Get the logger
LOG = log.get_logger(__name__)


class Test3(VMOptimizationBase):
    """Allows to test the optimization of the VMs."""

    def __init__(self):
        """Initialize the test connection."""
        self.metrics = None
        self.current_optimization = None
        self.current_distribution = None

    async def run(self, always):
        """Run the test VMs optimization."""

        while True:
            # Await the metrics to be recieved
            await self._wait_for_metrics()

            # Clear the current optimization
            self.current_optimization = None

            # Clear the current distribution
            self.current_distribution = None

            # Compute the optimization
            optimization = self._compute_algorithm()

            # Simulate a delay
            await trio.sleep(random.randint(1, 5))

            # Set the current optimization
            self.current_optimization = optimization

            # Reset the metrics
            self.metrics = None

            # If the optimization is not always running, break the loop
            if not always:
                break

    async def _wait_for_metrics(self):
        """Wait for the metrics to be recieved."""
        if self.metrics is None:
            LOG.debug("Waiting for metrics to be recieved.")
        while self.metrics is None:
            await trio.sleep(1)

    def _compute_algorithm(self):
        """Compute the optimization algorithm.

        - It has to consolidate the machines.

        :return: The distribution.
        :rtype: dict
        """
        # Dict of utilizations (Key: hostname, Value: utilization)
        utilizations = {}

        # Dict of list of VMs (Key: hostname, Value: list of VMs)
        distribution = {}

        # Get the utilization of each machine
        utilizations = self._get_utilizations(self.metrics)

        # Sort the machines by utilization
        sorted_machines = sorted(utilizations.items(), key=lambda x: x[1])

        # Get the VMs on each machine
        distribution = self._get_vms_on_machine(self.metrics)

        # Copy the distribution dict on the actual distribution
        self.current_distribution = copy.deepcopy(distribution)

        # Add the VMs on the machines with the lowest utilization to the machines with the highest utilization
        for i in range(len(sorted_machines) // 2):
            # If the sum of the lowest and highest utilization is less than 100%:
            if (
                utilizations[sorted_machines[i][0]]
                + utilizations[sorted_machines[-i - 1][0]]
                < 100
            ):
                # Add the VMs from the machine with the lowest utilization to the machine with the highest utilization
                for vm in distribution[sorted_machines[i][0]]:
                    distribution[sorted_machines[-i - 1][0]].append(vm)

                # Remove the VMs from the machine with the lowest utilization
                distribution[sorted_machines[i][0]] = []

        return distribution

    def _get_utilizations(self, metrics):
        """Get the utilization of each machine.

        :param metrics: The metrics.
        :type metrics: dict

        :return: The utilizations.
        :rtype: dict
        """
        utilizations = {}

        for hostname, value in metrics.items():
            for metric in value:
                if metric.name == "utilization":
                    # Get the utilization
                    utilizations[hostname] = self._get_utilization(metric)

        return utilizations

    def _get_utilization(self, metric):
        """Get the utilization of the machine.

        :param metric: The metric.
        :type metric: dict

        :return: The utilization.
        :rtype: float
        """
        # Get the value from the payload
        return float(json.loads(metric.payload)["value"])

    def _get_vms_on_machine(self, metrics):
        """Get the VMs on each machine.

        :param metrics: The metrics.
        :type metrics: dict

        :return: The VMs on each machine.
        :rtype: dict
        """
        # Create a dict of list of VMs (Key: hostname, Value: list of VMs)
        distribution = {}

        # Initialize the dict
        for hostname, value in metrics.items():
            distribution[hostname] = []

        # Get the VMs on each machine
        for hostname, value in metrics.items():
            for metric in value:
                if metric.name == "vms":
                    # Get the VMs as a dict
                    vms = self._get_vms(metric)
                    # Split the VMs into a list
                    for vm_uuid, vm in vms.items():
                        distribution[hostname].append({vm_uuid: vm})

        return distribution

    def _get_vms(self, metric):
        """Get the VMs on the machine.

        :param metric: The metric.
        :type metric: dict

        :return: The VMs.
        :rtype: list
        """
        # Get the value from the payload and convert it to a dict
        return json.loads(metric.payload)

    def recieve_metrics(self, metrics):
        """Recieve the metrics from the manager.

        :param metrics: The metrics.
        :type metrics: dict
        """
        LOG.debug("Metrics revieved in the optimization plugin.")
        # Set the metrics
        self.metrics = metrics

    async def get_optimization(self):
        """Get the optimization result.

        :return: The optimization result.
        :rtype: dict
        """
        if self.current_optimization is None:
            LOG.debug("Waiting for optimization to be calculated.")
        while self.current_optimization is None:
            await trio.sleep(1)

        # Log the optimization
        LOG.debug("Obtained VM optimization.")
        rich.print(self.current_optimization)

        return self.current_optimization

    async def get_current_distribution(self):
        """Get the current distribution of VMs.

        :return: The current distribution of VMs.
        :rtype: dict
        """
        if self.current_distribution is None:
            LOG.debug("Waiting for distribution to be calculated.")
        while self.current_distribution is None:
            await trio.sleep(1)

        # Log the distribution
        LOG.debug("Obtained current distribution.")
        rich.print(self.current_distribution)

        return self.current_distribution
