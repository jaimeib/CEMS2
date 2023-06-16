"""PM Optimization Manager module."""

import trio

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the PM Optimizations."""

    def __init__(self):
        """Initialize the PM optimization manager."""
        # Running PM optimizations
        self.running_pm_optimizations = []

        # Last metrics recieved
        self.last_metrics = None

        # Last baseline recieved
        self.last_baseline = None

        # Obtain the list of PM optimizations configured in the config file
        self.default_pm_optimization_name = CONFIG.get(
            "machines_control.plugins", "default_pm_optimization"
        )

        # Check if the default PM optimization is installed
        if (
            self.default_pm_optimization_name
            not in plugin_loader.get_pm_optimizations_names()
        ):
            LOG.error(
                "PM Optimization plugin '%s' is not installed.",
                self.default_pm_optimization_name,
            )
            raise RuntimeError(
                f"PM Optimization plugin '{self.default_pm_optimization_name}' is not installed."
            )

        # Get the default PM optimization from the plugin loader
        default_pm_optimization = plugin_loader.get_pm_optimizations()[
            self.default_pm_optimization_name
        ]
        self.default_pm_optimization = default_pm_optimization()
        self.running_pm_optimizations.append(self.default_pm_optimization)
        LOG.debug(
            "Default PM Optimizations loaded: %s",
            self.default_pm_optimization_name,
        )

        # Get all the PM optimizations from the plugin loader
        self.pm_optimizations = [
            (i, plugin_loader.get_pm_optimizations()[i])
            for i in plugin_loader.get_pm_optimizations_names()
        ]
        LOG.debug(
            "PM Optimizations loaded: %s",
            list(plugin_loader.get_pm_optimizations_names()),
        )

    def new_metrics(self, new_metrics):
        """Pass the new metrics to the running PM optimizations.

        :param new_metrics: new metrics
        :type new_metrics: dict
        """
        for pm_optimization in self.running_pm_optimizations:
            pm_optimization.recieve_metrics(new_metrics)
        self.last_metrics = new_metrics

    def new_baseline(self, new_baseline):
        """Pass the new baseline to the running PM optimizations.

        :param new_baseline: new baseline
        :type new_baseline: dict
        """
        for pm_optimization in self.running_pm_optimizations:
            pm_optimization.recieve_baseline(new_baseline)
        self.last_baseline = new_baseline

    async def get_default_optimization(self):
        """Get the default PM optimization.

        :return: A dict with the result of the optimization
        :rtype: dict
        """
        return await self.default_pm_optimization.get_optimization()

    def get_installed_plugins(self):
        """Get the list of installed PM optimizations.

        :return: The list of installed PM optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_pm_optimizations_names()

    async def get_pm_optimizations(self, name: str = None):
        """Get the PM optimizations.

        :param name: The name of the PM optimization to get
        :type name: str

        :return: The PM optimizations
        :rtype: dict[str, dict]
        """
        # Create a dict to store the PM optimizations
        optimizations = {}

        # Run the rest of the PM optimizations (not the default one)
        async with trio.open_nursery() as nursery:
            for pm_optimization_name, pm_optimization_cls in self.pm_optimizations:
                # Skip the default PM optimization
                if pm_optimization_name == self.default_pm_optimization_name:
                    continue

                # Skip the PM optimization if it is not the one we want
                if name is not None and name != pm_optimization_name:
                    continue

                # Run the PM optimization as an async task
                nursery.start_soon(
                    self._run_pm_optimization,
                    pm_optimization_name,
                    pm_optimization_cls,
                    False,
                    optimizations,
                )

        # Get the default PM optimization result if requested
        if name is None or name == self.default_pm_optimization_name:
            optimizations[
                self.default_pm_optimization_name
            ] = await self.get_default_optimization()

        # Return the PM optimizations
        return optimizations

    async def _run_pm_optimization(
        self, pm_optimization_name, pm_optimization_cls, always, optimizations
    ):
        """Run a PM optimization.

        :param pm_optimization_name: The name of the PM optimization to run
        :type pm_optimization_name: str

        :param pm_optimization_cls: The class of the PM optimization to run
        :type pm_optimization_cls: class

        :param always: If the PM optimization should always run
        :type always: bool

        :param optimizations: The dict to store the optimizations
        :type optimizations: dict[str, dict]
        """
        # Create the PM optimization
        pm_optimization = pm_optimization_cls()

        # Add the PM optimization to the list of running PM optimizations
        self.running_pm_optimizations.append(pm_optimization)

        # Pass the last metrics available to the PM optimization
        if self.last_metrics is not None:
            pm_optimization.recieve_metrics(self.last_metrics)

        # Pass the last baseline available to the PM optimization
        if self.last_baseline is not None:
            pm_optimization.recieve_baseline(self.last_baseline)

        # Run the PM optimization
        await pm_optimization.run(always)

        # Get the result of the PM optimization
        optimizations[pm_optimization_name] = await pm_optimization.get_optimization()

        # Remove the PM optimization from the list of running PM optimizations
        self.running_pm_optimizations.remove(pm_optimization)
