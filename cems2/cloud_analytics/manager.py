"""cloud_analytics manager module."""

import time

import cems2.cloud_analytics.collector.manager as collector_manager
import cems2.cloud_analytics.reporter.manager as reporter_manager
from cems2 import config_loader, log
from cems2.schemas.machine import Machine  # TODO: To test

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Cloud Analytics Manager class.

    This class is responsible for:
    - Obtaining the metrics from the collector manager
    - Forwarding the metrics to the reporter manager
    """

    def __init__(self):
        """Initialize the manager."""
        self.collector = None
        self.reporter = None

        # List of machines to monitor
        self.machines_monitoring = [
            Machine(
                groupname="all",
                hostname="all1",
                id=1,
                management_ip="192.168.56.107",
                management_username="ubuntu",
                brand_model="HP ProLiant DL360 Gen10",
                management_password="ubuntu",
            )
        ]

        # Dictionary to store the last metrics of each machine
        # (key: hostname, value: list of metrics)
        self.metrics = {}

        # Monitoring interval
        self.monitoring_interval = None

    def load_managers(self):
        """Load the managers required by the cloud_analytics manager."""
        self.collector = collector_manager.Manager()
        self.reporter = reporter_manager.Manager()

    def set_machines(self, machines_list):
        """Update the machines to monitor.

        :param machines_list: list of machines to monitor
        :type machines_list: list[Machine]
        """

        self.machines_monitoring.append(machines_list)
        LOG.info(
            "Machines to monitor: %s", [machine.hostname for machine in machines_list]
        )

    def set_monitoring_interval(self):
        """Set the monitoring interval for the Analytics Manager."""
        self.monitoring_interval = CONFIG.getint("cloud_analytics", "interval")
        LOG.info("Monitoring interval set to %s", self.monitoring_interval)

    def run(self):
        """Run the cloud_analytics manager.

        - Load the managers
        - Get the metrics from the collector manager
        - Send the metrics to the reporter manager
        """
        # Load the managers
        self.load_managers()

        # Set the monitoring interval
        self.set_monitoring_interval()

        # Run periodically as the monitoring interval
        while True:
            # For each machine to monitor
            for machine in self.machines_monitoring:
                # Get the metrics from the collector manager
                self.metrics[machine.hostname] = self.collector.get_metrics(
                    machine.hostname
                )

                # Send the metrics to the reporter manager
                self.reporter.send_metrics(self.metrics[machine.hostname])

            # Wait the monitoring interval
            LOG.debug("Waiting %s seconds", self.monitoring_interval)
            time.sleep(self.monitoring_interval)

    # Communication with de API monitoring controller
    def obtain_last_metrics(self):
        """Obtain the last metrics of each machine.

        :return: dictionary with the last metrics of each machine
        :rtype: dict{key: hostname, value: list[Metric]}
        """
        return self.metrics
