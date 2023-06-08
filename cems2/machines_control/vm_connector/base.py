"""Base class for VMs Connector plug-ins."""

from abc import ABCMeta, abstractmethod


class VMConnectorBase(metaclass=ABCMeta):
    """Allows to connect to the cloud management system to manage VMs."""

    @abstractmethod
    def __init__(self):
        """Initialize the connection to the VMs."""

    @abstractmethod
    async def migrate_vm(self, vm_id, pm_hostname):
        """Migrate the VM to the PM.

        :param vm_id: The ID of the VM
        :type vm_id: str

        :param pm_hostname: The hostname of the dest PM
        :type pm_hostname: str
        """
