"""CEMS2 Launcher."""

from functools import partial

import trio
import uvicorn

import cems2.API.api as api
from cems2 import log
from cems2.API.routes.monitoring import monitoring_controller
from cems2.cloud_analytics.manager import Manager as CloudAnalyticsManager
from cems2.machines_control.manager import Manager as MachinesControlManager

LOG = log.get_logger(__name__)


async def start_api():
    """Start the API server."""
    LOG.info("Starting API server")

    # Run the API server in a separate thread
    await trio.to_thread.run_sync(
        partial(uvicorn.run, api.api, host="localhost", port=8000)
    )

    # If the API server stops, log it
    LOG.error("API server stopped")


async def start_cloud_analytics_manager(cloud_analytics_manager):
    """Start the Cloud Analytics Manager."""
    LOG.info("Starting Cloud Analytics Manager")

    # Run the Cloud Analytics Manager in a separate thread
    await trio.to_thread.run_sync(cloud_analytics_manager.run)

    # If the Cloud Analytics Manager stops, log it
    LOG.error("Cloud Analytics Manager stopped")


async def start_machines_control_manager(machines_control_manager):
    """Start the Machine Control Manager."""
    LOG.info("Starting Machine Control Manager")

    # Run the Machine Control Manager in a separate thread
    await trio.to_thread.run_sync(machines_control_manager.run)

    # If the Machine Control Manager stops, log it
    LOG.error("Machine Control Manager stopped")


async def main():
    """Main function.
    - Start the API
    - Start the Cloud Analytics Manager
    - Start the Machine Control Manager
    """
    LOG.info("Starting CEMS2")

    # Create the Cloud Analytics Manager
    cloud_analytics_manager = CloudAnalyticsManager()
    print("MAIN:", id(cloud_analytics_manager))
    print("MAIN:", cloud_analytics_manager)

    # Pass the cloud_analytics_manager to the monitoring manager
    monitoring_controller.set_cloud_analytics_manager(cloud_analytics_manager)

    # Create 3 tasks to run in parallel
    async with trio.open_nursery() as nursery:
        # Start the API (Task 1)
        nursery.start_soon(start_api)
        # Start the Cloud Analytics Manager (Task 2)
        nursery.start_soon(start_cloud_analytics_manager, cloud_analytics_manager)
        # Start the Machine Control Manager (Task 3)
        # nursery.start_soon(start_machines_control_manager, machines_control_manager)


if __name__ == "__main__":
    # Run the main function using Trio
    trio.run(main)
