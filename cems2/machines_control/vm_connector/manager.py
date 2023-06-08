"""VM Connector Manager module."""

import trio

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """ "Manager for the VM Connectors."""

    def __init__(self):
        """Initialize the VM connector manager."""
        # Obtain the list of VM connectors configured in the config file
        vm_connectors_list = CONFIG.getlist("machines_control.plugins", "vm_connectors")

        # Check if the VM connectors are installed
        for vm_connector in vm_connectors_list:
            if vm_connector not in plugin_loader.get_vm_connectors_names():
                LOG.error(
                    "VM Connector plugin '%s' is not installed.",
                    vm_connector,
                )
                raise Exception(
                    f"VM Connector plugin '{vm_connector}' is not installed."
                )
        # Get the VM connectors from the plugin loader
        vm_connectors = [
            (i, plugin_loader.get_vm_connectors()[i]) for i in vm_connectors_list
        ]

        # Create an instance of each VM connector (Only one object for each connector)
        vm_connectors = [(i, j()) for i, j in vm_connectors]

        self.vm_connectors = vm_connectors
        LOG.debug("VM Connectors loaded: %s", vm_connectors_list)

        # Set the VM connector plugin timeout
        self.timeout = CONFIG.getint("machines_control", "vm_connector_timeout")

    async def apply_optimization(self, current_dist: dict, optimization: dict):
        """Apply the VM optimization.

        :param current_dist: The current distribution of VMs
        :type current_dist: dict
        :param optimization: The optimization to apply
        :type optimization: dict
        """

        # Remove from the optimization the VMs that are already in the correct PM
        for pm in optimization:
            for vm in optimization[pm]:
                if vm in current_dist[pm]:
                    optimization[pm].remove(vm)

        # Migrate the VMs
        for pm in optimization:
            # If there are no VMs to migrate
            if len(optimization[pm]) == 0:
                continue

            # Set a timeout for the migration of the VMs
            with trio.fail_after(self.timeout) as cancel_scope:
                # Creates an async task for each PM
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(self._migrate_vms, optimization[pm], pm)

            # If the timeout is reached
            if cancel_scope.cancelled_caught:
                LOG.error(
                    "Timeout reached while migrating VMs to PM '%s'.",
                    pm,
                )
                raise Exception(f"Timeout reached while migrating VMs to PM '{pm}'.")

    async def _migrate_vms(self, vms: list, pm_hostname: str):
        """Migrate the VMs to the PM.

        :param vms: The VMs to migrate
        :type vms: list
        :param pm_hostname: The hostname of the PM
        :type pm_hostname: str
        """
        # Get the VM connector
        vm_connector = self._get_vm_connector(vms)

        # Migrate the VMs
        for vm in vms:
            await vm_connector.migrate_vm(vm, pm_hostname)

    def _get_vm_connector(self, vms: list):
        """Get the VM connector for the VM.

        :param vms: The VM
        :type vms: list
        """

        # Get the VM connector name from the VM metadata
        vms_connector_name = list(vms[0].values())[0]["managed_by"]

        # Check that all the VMs are managed by the same VM connector
        for vm in vms:
            if list(vm.values())[0]["managed_by"] != vms_connector_name:
                LOG.error(
                    "VMs are managed by different VM connectors.",
                )
                raise Exception(f"VMs are managed by different VM connectors.")

        # Get the VM connector
        plugin = None
        for vm_connector_name, vm_connector in self.vm_connectors:
            if vm_connector_name == vms_connector_name:
                plugin = vm_connector

        # If the VM connector is not found
        if plugin is None:
            LOG.error(
                "VM connector '%s' not found.",
                vms_connector_name,
            )
            raise Exception(f"VM connector '{vms_connector_name}' not found.")

        return plugin

    def get_installed_plugins(self):
        """Get the list of installed VM connectors.

        :return: The list of installed VM connectors
        :rtype: list[str]
        """
        return plugin_loader.get_vm_connectors_names()
