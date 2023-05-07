"""Module to load the plug-ins into the Machines Control Application."""

import stevedore

VM_OPTIMIZATION_NAMESPACE = "cems2.machines_control.vm_optimization"
PM_OPTIMIZATION_NAMESPACE = "cems2.machines_control.pm_optimization"
VM_CONNECTOR_NAMESPACE = "cems2.machines_control.vm_connector"
PM_CONNECTOR_NAMESPACE = "cems2.machines_control.pm_connector"


def _get_names(namespace):
    """Get the names of the plug-ins in the specified namespace.

    :param namespace: The namespace to search for plug-ins
    :type namespace: str

    :return: The names of the plug-ins in the specified namespace
    :rtype: frozenset
    """
    mgr = stevedore.ExtensionManager(namespace=namespace)
    return frozenset(mgr.names())


def _get_extensions(namespace):
    """Get the extensions of the plug-ins in the specified namespace.

    :param namespace: The namespace to search for plug-ins
    :type namespace: str

    :return: The extensions of the plug-ins in the specified namespace
    :rtype: dict
    """
    mgr = stevedore.ExtensionManager(namespace=namespace, propagate_map_exceptions=True)
    return dict(mgr.map(lambda ext: (ext.entry_point.name, ext.plugin)))


def get_vm_optimizations_names():
    """Get the names of the VM optimizations.

    :return: The names of the VM optimizations
    :rtype: frozenset
    """
    return _get_names(VM_OPTIMIZATION_NAMESPACE)


def get_vm_optimizations():
    """Get the VM optimizations.

    :return: The VM optimizations
    :rtype: dict
    """
    return _get_extensions(VM_OPTIMIZATION_NAMESPACE)


def get_pm_optimizations_names():
    """Get the names of the PM optimizations.

    :return: The names of the PM optimizations
    :rtype: frozenset
    """
    return _get_names(PM_OPTIMIZATION_NAMESPACE)


def get_pm_optimizations():
    """Get the PM optimizations.

    :return: The PM optimizations
    :rtype: dict
    """
    return _get_extensions(PM_OPTIMIZATION_NAMESPACE)


def get_vm_connectors_names():
    """Get the names of the VM connectors.

    :return: The names of the VM connectors
    :rtype: frozenset
    """
    return _get_names(VM_CONNECTOR_NAMESPACE)


def get_vm_connectors():
    """Get the VM connectors.

    :return: The VM connectors
    :rtype: dict
    """
    return _get_extensions(VM_CONNECTOR_NAMESPACE)


def get_pm_connectors_names():
    """Get the names of the PM connectors.

    :return: The names of the PM connectors
    :rtype: frozenset
    """
    return _get_names(PM_CONNECTOR_NAMESPACE)


def get_pm_connectors():
    """Get the PM connectors.

    :return: The PM connectors
    :rtype: dict
    """
    return _get_extensions(PM_CONNECTOR_NAMESPACE)
