"""CEMS2 Launcher."""

import multiprocessing

from cems2 import log
from cems2.cloud_analytics.manager import Manager as CloudAnalyticsManager
from cems2.machines_control.manager import Manager as MachinesControlManager

LOG = log.get_logger(__name__)


def main():
    """Main function.
    - Start the Cloud Analytics Manager
    - Start the Machine Control Manager
    """
    LOG.info("Starting CEMS2")

    # Cloud Analytics Manager Process
    cloud_analytics_manager = CloudAnalyticsManager()
    cloud_analytics_process = multiprocessing.Process(
        target=cloud_analytics_manager.run
    )
    cloud_analytics_process.start()
    LOG.info("Cloud Analytics Manager started")

    # Machines Control Manager Process
    machines_control_manager = MachinesControlManager()
    machines_control_process = multiprocessing.Process(
        target=machines_control_manager.run
    )
    machines_control_process.start()
    LOG.info("Machine Control Manager started")


if __name__ == "__main__":
    main()
