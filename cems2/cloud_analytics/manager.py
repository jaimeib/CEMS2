"""
cloud_analytics manager module
"""

import cems2.cloud_analytics.collector.manager as collector_manager
import cems2.cloud_analytics.reporter.manager as reporter_manager


class Manager(object):
    """
    cloud_analytics manager class to orchestrate the collection of metrics from
    the cloud infrastructure and their forwarding to other systems
    """

    def __init__(self):
        """
        Initialize the manager
        """

        self.collector = None
        self.reporter = None

    def load_managers(self):
        """
        Load the managers required by the cloud_analytics manager
        """

        self.collector = collector_manager.Manager()
        self.reporter = reporter_manager.Manager()

    def get_machines_monitoring(self):
        """
        Get the list of machines to monitor from the API (#FIXME: From the monitoring controller or the Machine Manager)
        """

        # TODO: Communication with the API??

    def run(self):
        """
        Run the cloud_analytics manager

        - Load the managers
        - Get the metrics from the collector manager
        - Send the metrics to the reporter manager
        """

        # Load the managers
        self.load_managers()

        # For each machine to monitor
        for machine in self.get_machines_monitoring():
            # Get the metrics from the collector manager
            metrics = self.collector.get_metrics(machine.hostname)

            # Send the metrics to the reporter manager
            self.reporter.send_metrics(metrics)

        # Comunicate with the API to send the metrics if required

        # TODO: Communication with the API??

        # TODO: Usign API Schemas to validate the data of the metrics o other internal schema?
