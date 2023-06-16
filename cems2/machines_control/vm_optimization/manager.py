"""VM Optimization Manager module."""

import trio

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the VM Optimizations."""

    def __init__(self):
        """Initialize the VM optimization manager."""
        # Running VM optimizations
        self.running_vm_optimizations = []

        # Last metrics recieved
        self.last_metrics = None

        # Obtain the default VM optimization configured in the config file
        self.default_vm_optimization_name = CONFIG.get(
            "machines_control.plugins", "default_vm_optimization"
        )

        # Check if the default VM optimization is installed
        if (
            self.default_vm_optimization_name
            not in plugin_loader.get_vm_optimizations_names()
        ):
            LOG.error(
                "VM Optimization plugin '%s' is not installed.",
                self.default_vm_optimization_name,
            )
            raise RuntimeError(
                f"VM Optimization plugin '{self.default_vm_optimization_name}' is not installed."
            )

        # Get the default VM optimization from the plugin loader
        default_vm_optimization = plugin_loader.get_vm_optimizations()[
            self.default_vm_optimization_name
        ]
        self.default_vm_optimization = default_vm_optimization()
        self.running_vm_optimizations.append(self.default_vm_optimization)
        LOG.debug(
            "Default VM Optimizations loaded: %s",
            self.default_vm_optimization_name,
        )

        # Get all the VM optimizations from the plugin loader
        self.vm_optimizations = [
            (i, plugin_loader.get_vm_optimizations()[i])
            for i in plugin_loader.get_vm_optimizations_names()
        ]
        LOG.debug(
            "VM Optimizations loaded: %s",
            list(plugin_loader.get_vm_optimizations_names()),
        )

    def new_metrics(self, new_metrics):
        """Pass the new metrics to the running optimizations.

        :param new_metrics: new metrics
        :type new_metrics: dict
        """
        for vm_optimization in self.running_vm_optimizations:
            vm_optimization.recieve_metrics(new_metrics)
        self.last_metrics = new_metrics

    async def get_default_optimization(self):
        """Get the default VM optimization.

        :return: A dict with the result of the optimization
        :rtype: dict
        """
        return await self.default_vm_optimization.get_optimization()

    async def get_current_distribution(self):
        """Get the current distribution of VMs.

        :return: A dict with the current distribution of VMs
        :rtype: dict
        """
        return await self.default_vm_optimization.get_current_distribution()

    def get_installed_plugins(self):
        """Get the list of installed VM optimizations.

        :return: The list of installed VM optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_vm_optimizations_names()

    async def get_vm_optimizations(self, name: str):
        """Get the VM optimizations.

        :param name: Name of the VM optimization to get
        :type name: str

        :return: The VM optimizations
        :rtype: dict[str, dict]
        """
        # Create a dict to store the VM optimizations
        optimizations = {}

        # Run the rest of the VM optimizations (except the default one)
        async with trio.open_nursery() as nursery:
            for vm_optimization_name, vm_optimization_cls in self.vm_optimizations:
                # Skip the default VM optimization
                if vm_optimization_name == self.default_vm_optimization_name:
                    continue

                # Skip the VM optimization if it is not the one requested
                if name is not None and name != vm_optimization_name:
                    continue

                # Run an async task to run the VM optimization
                nursery.start_soon(
                    self._run_vm_optimization,
                    vm_optimization_name,
                    vm_optimization_cls,
                    False,
                    optimizations,
                )

        # Get the default VM optimization result if it is requested
        if name is None or name == self.default_vm_optimization_name:
            optimizations[
                self.default_vm_optimization_name
            ] = await self.get_default_optimization()

        # Return the VM optimizations
        return optimizations

    async def _run_vm_optimization(
        self, vm_optimization_name, vm_optimization_cls, always, optimizations
    ):
        """Run the VM optimization.

        :param vm_optimization_name: Name of the VM optimization
        :type vm_optimization_name: str

        :param vm_optimization_cls: Class of the VM optimization
        :type vm_optimization_cls: class

        :param always: If the optimization should run always
        :type always: bool

        :param optimizations: Dict to store the result of the optimization
        :type optimizations: dict
        """
        # Create the VM optimization
        vm_optimization = vm_optimization_cls()

        # Add the VM optimization to the running VM optimizations
        self.running_vm_optimizations.append(vm_optimization)

        # Pass the last metrics available to the optimization
        if self.last_metrics is not None:
            vm_optimization.recieve_metrics(self.last_metrics)

        # Run the optimization
        await vm_optimization.run(always)

        # Get the result of the optimization
        optimizations[vm_optimization_name] = await vm_optimization.get_optimization()

        # Remove the VM optimization from the running VM optimizations
        self.running_vm_optimizations.remove(vm_optimization)
