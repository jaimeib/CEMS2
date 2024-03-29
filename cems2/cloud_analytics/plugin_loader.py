"""Module to load the plug-ins into the Cloud Analytics Application."""

import stevedore

COLLECTOR_NAMESPACE = "cems2.cloud_analytics.collector"
REPORTER_NAMESPACE = "cems2.cloud_analytics.reporter"


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


def get_collectors_names():
    """Get the names of the collectors.

    :return: The names of the collectors
    :rtype: frozenset
    """
    return _get_names(COLLECTOR_NAMESPACE)


def get_collectors():
    """Get the collectors.

    :return: The collectors
    :rtype: dict
    """
    return _get_extensions(COLLECTOR_NAMESPACE)


def get_reporters_names():
    """Get the names of the reporters.

    :return: The names of the reporters
    :rtype: frozenset
    """
    return _get_names(REPORTER_NAMESPACE)


def get_reporters():
    """Get the reporters.

    :return: The reporters
    :rtype: dict
    """
    return _get_extensions(REPORTER_NAMESPACE)
