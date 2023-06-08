"""CEMS2 Launcher."""

import signal
import sys
from functools import partial

import trio
import uvicorn

import cems2.API.api as api
from cems2 import log
from cems2.API.routes.actions import actions_controller
from cems2.API.routes.machine import machine_manager
from cems2.API.routes.monitoring import monitoring_controller
from cems2.cloud_analytics.manager import Manager as CloudAnalyticsManager
from cems2.machines_control.manager import Manager as MachinesControlManager

LOG = log.get_logger(__name__)

api_cancel_scope = trio.CancelScope()
cloud_analytics_manager_cancel_scope = trio.CancelScope()
machines_control_manager_cancel_scope = trio.CancelScope()


def shutdown():
    """Shutdown function."""
    api_cancel_scope.cancel()
    cloud_analytics_manager_cancel_scope.cancel()
    machines_control_manager_cancel_scope.cancel()
    LOG.info("Shutting down CEMS2")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown)  # Register the shutdown function to the SIGTERM
signal.signal(signal.SIGINT, shutdown)  # Register the shutdown function to the SIGINT


async def start_api():
    """Start the API server."""
    with api_cancel_scope:
        LOG.info("Starting API server")

        # Run the API server in a separate thread
        await trio.to_thread.run_sync(
            partial(uvicorn.run, api.api, host="localhost", port=8000)
        )
        # If the API server stops, log it
        LOG.error("API server stopped")


async def start_cloud_analytics_manager(cloud_analytics_manager):
    """Start the Cloud Analytics Manager."""
    with cloud_analytics_manager_cancel_scope:
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


async def async_main():
    """Main function.
    - Start the API
    - Start the Cloud Analytics Manager
    - Start the Machine Control Manager
    """
    LOG.info("Starting CEMS2")

    # Load the monitoring controller to the machine manager
    machine_manager.set_monitoring_controller(monitoring_controller)

    # Load the actions controller to the machine manager
    machine_manager.set_actions_controller(actions_controller)

    # Load the machine manager to the monitoring controller
    monitoring_controller.set_machine_manager(machine_manager)

    # Load the actions controller to the monitoring controller
    monitoring_controller.set_actions_controller(actions_controller)

    # Create the Cloud Analytics Manager
    cloud_analytics_manager = CloudAnalyticsManager()

    # Load the cloud_analytics_manager to the monitoring manager
    monitoring_controller.set_cloud_analytics_manager(cloud_analytics_manager)

    # Load the monitoring controller to the actions manager
    actions_controller.set_monitoring_controller(monitoring_controller)

    # Load the machine manager to the actions manager
    actions_controller.set_machine_manager(machine_manager)

    # Create the Machine Control Manager
    machines_control_manager = MachinesControlManager()

    # Load the machines_control_manager to the actions manager
    actions_controller.set_machines_control_manager(machines_control_manager)

    # Create 3 tasks to run in parallel
    async with trio.open_nursery() as nursery:
        # Start the API (Task 1)
        nursery.start_soon(start_api)
        # Start the Cloud Analytics Manager (Task 2)
        nursery.start_soon(start_cloud_analytics_manager, cloud_analytics_manager)
        # Start the Machine Control Manager (Task 3)
        nursery.start_soon(start_machines_control_manager, machines_control_manager)


def main():
    """Main function."""
    # Run the async_main function using Trio
    trio.run(async_main)


if __name__ == "__main__":
    main()
