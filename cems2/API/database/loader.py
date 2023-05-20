"""Module to load the initial data .yaml file into the database."""

import ipaddress

import yaml
from yaml.loader import SafeLoader

from cems2 import log
from cems2.API.database.config import create_tables, get_db
from cems2.API.models.machine import Machines
from cems2.schemas.machine import BaseMachine

pending_hosts = []  # List of hosts not updated because the ip already exists previously

# Get the logger
LOG = log.get_logger(__name__)


def load_hosts(datafile):
    """Load the initial data .yaml file into the database."""
    LOG.info("Loading the hosts.yaml file into the database.")

    # Create the tables in the database
    create_tables()

    # Obtain the list of groups from the file
    group_list = _read_groups(datafile)

    # Convert the list of groups to a list of hosts (BaseMachine objects)
    hosts_list = _convert_groups_to_hosts(group_list)

    # Update the database table with the hosts from the hosts.yaml file
    _update_hosts(hosts_list)

    # Update the available machines in the database
    _update_available_machines(hosts_list)

    LOG.info("The hosts.yaml file has been loaded into the database.")


def _read_groups(file):
    """Read the groups from the file.

    :return: List of groups
    :rtype: list[dict]
    """
    with open(file, "r") as stream:
        try:
            groups = yaml.load(stream, Loader=SafeLoader)
            return groups
        except yaml.YAMLError as exc:
            print(exc)


def _convert_groups_to_hosts(groups):
    """Convert the list of groups to a list of machines (BaseMachine).

    :param groups: List of groups
    :type groups: list[dict]

    :return: List of hosts
    :rtype: list[BaseMachine]
    """
    # List of hosts obtained from the groups
    hosts_obtained_from_group = []

    # For each group, create a list of hosts
    for group in groups:
        new_group_list = _create_hosts_list(group)

        # Add particular hosts atributtes to each host
        if "hosts" in group:  # If the group has particular hosts
            for host in group["hosts"]:  # For each particular host
                _find_particular_atributtes(new_group_list, host)

        # If the group has been created correctly, add it to the list of groups
        if new_group_list:
            hosts_obtained_from_group.append(new_group_list)

    # Flatten the list of lists of hosts to a list of hosts
    hosts_obtained_from_group = [
        host for sublist in hosts_obtained_from_group for host in sublist
    ]

    return hosts_obtained_from_group


# Aux functions to parse the initial data .yaml file


def _create_hosts_list(group):
    """Create a list of hosts from a group.

    :param group: Group
    :type group: dict

    :return: List of hosts
    :rtype: list[BaseMachine]
    """
    # Check for consistency of the hostname and the groupname
    if not _check_hostname_consistency(group):
        return []  # Return an empty list

    # Check that the number of hosts is equal to the number of IPs
    if not _check_number_of_hosts_and_ips(group):
        return []  # Return an empty list

    # If the group has only one host, create a list with one host
    if len(group["hostname_range"]) == 1:
        host = BaseMachine(
            groupname=group["groupname"],
            hostname=str(group["hostname_range"][0]),
            brand_model=group["brand_model"],
            management_ip=group["management_ip_range"][0],
            management_username=group["management_username"],
            management_password=group["management_password"],
            connector=group["connector"],
            monitoring=False,  # By default, the machine is unmonitored
            available=True,  # By default, the machine is available
        )
        return [host]

    # Get the first hostname of the range
    first_hostname = str(group["hostname_range"][0])

    # Get the last hostname of the range
    last_hostname = str(group["hostname_range"][1])

    # Obtain the indexes of the first and last hostname of the range
    # The index is obtained by removing the groupname from the hostname
    first_index = int(first_hostname.replace(group["groupname"], ""))
    last_index = int(last_hostname.replace(group["groupname"], ""))

    # Get the first IP of the range
    first_ip = ipaddress.IPv4Address(group["management_ip_range"][0])
    # Get the last IP of the range
    last_ip = ipaddress.IPv4Address(group["management_ip_range"][1])

    new_hosts_list = []

    # Create a list of hosts with the hostname and management_ip
    for i in range(first_index, last_index + 1):
        # Check if the IP is on the range (for ensuring that the range is not full)
        if first_ip > last_ip:
            LOG.error(
                f"The range of the group {group['groupname']} is full. The IP {first_ip} is out of the range."
            )
            return []  # Return an empty list
        else:
            # Generate the hostname in the same format as the hostname_range (same number of digits)
            hostname = group["groupname"] + str(i).zfill(
                len(first_hostname) - len(group["groupname"])
            )

            host = BaseMachine(
                groupname=group["groupname"],
                hostname=hostname,
                brand_model=group["brand_model"],
                management_ip=str(first_ip),
                management_username=group["management_username"],
                management_password=group["management_password"],
                connector=group["connector"],
                monitoring=False,  # By default, the machine is unmonitored
                available=True,  # By default, the machine is available
            )
            new_hosts_list.append(host)
            first_ip += 1

    return new_hosts_list


def _check_hostname_consistency(group):
    """Check if the hostname is consistent with the groupname.

    :param group: Group with the hosts to check the consistency of the hostname
    :type group: dict

    :return: True if the hostname is consistent with the groupname, False otherwise
    :rtype: bool
    """
    if (group["hostname_range"][0])[: len(group["groupname"])] != group["groupname"]:
        LOG.error(
            f"The hostname of the group {group['groupname']} is not consistent with the groupname."
        )
        return False
    else:
        return True


def _check_number_of_hosts_and_ips(group):
    """Check if the number of hosts is equal to the number of IPs.

    :param group: Group to check the number of hosts and IPs
    :type group: dict

    :return: True if the number of hosts is equal to the number of IPs, False otherwise
    :rtype: bool
    """
    # If there is only one host, check that there is only one IP
    if len(group["hostname_range"]) == 1 and len(group["management_ip_range"]) != 1:
        LOG.error(
            f"The group {group['groupname']} has only one host but more than one IP."
        )
        return False

    # If there is only one IP, check that there is only one host
    if len(group["hostname_range"]) != 1 and len(group["management_ip_range"]) == 1:
        LOG.error(
            f"The group {group['groupname']} has more than one host but only one IP."
        )
        return False

    # If there is only one host and one IP, return True
    if len(group["hostname_range"]) == 1 and len(group["management_ip_range"]) == 1:
        return True

    # Get the first hostname of the range
    first_hostname = str(group["hostname_range"][0])

    # Get the last hostname of the range
    last_hostname = str(group["hostname_range"][1])

    # Obtain the indexes of the first and last hostname of the range
    # The index is obtained by removing the groupname from the hostname
    first_index = int(first_hostname.replace(group["groupname"], ""))
    last_index = int(last_hostname.replace(group["groupname"], ""))

    # Get the first IP of the range
    first_ip = ipaddress.IPv4Address(group["management_ip_range"][0])
    # Get the last IP of the range
    last_ip = ipaddress.IPv4Address(group["management_ip_range"][1])

    # Check that the number of hosts is equal to the number of IPs
    if last_index - first_index != (int(last_ip) - int(first_ip)):
        LOG.error(
            f"The number of hosts of the group {group['groupname']} is not equal to the number of IPs."
        )
        return False
    else:
        return True


def _find_particular_atributtes(hosts, host):
    """Find the particular atributtes of a host and add them to the host.

    :param hosts: List of hosts
    :type hosts: list

    :param host: Host to find the particular atributtes
    :type host: dict
    """
    # If the host has a particular brand_model, add it to the host
    if "brand_model" in host:
        _update_brand_model(hosts, host)
    # If the host has a particular management_ip, add it to the host
    if "management_ip" in host:
        _update_management_ip(hosts, host)
    # If the host has a particular management_username, add it to the host
    if "management_username" in host:
        _update_management_username(hosts, host)
    # If the host has a particular management_password, add it to the host
    if "management_password" in host:
        _update_management_password(hosts, host)
    # If the host has a particular connector, add it to the host
    if "connector" in host:
        _update_connector(hosts, host)


def _update_brand_model(hosts, host):
    """Update the brand_model of the host.

    :param hosts: List of hosts
    :type hosts: list

    :param host: Host to update the brand_model
    :type host: dict
    """
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.brand_model = host["brand_model"]
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        LOG.error(
            f"The host {host['hostname']} does not exist, when looking for brand_model."
        )


def _update_management_ip(hosts, host):
    """Update the management_ip of the host.

    :param hosts: List of hosts
    :type hosts: list

    :param host: Host to update the management_ip
    :type host: dict
    """
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.management_ip = host["management_ip"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        LOG.error(
            f"The host {host['hostname']} does not exist, when looking for management_ip."
        )


def _update_management_username(hosts, host):
    """Update the management_username of the host.

    :param hosts: List of hosts
    :type hosts: list

    :param host: Host to update the management_username
    :type host: dict
    """
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.management_username = host["management_username"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        LOG.error(
            f"The host {host['hostname']} does not exist, when looking for management_username."
        )


def _update_management_password(hosts, host):
    """Update the management_password of the host.

    :param hosts: List of hosts
    :type hosts: list

    :param host: Host to update the management_password
    :type host: dict
    """
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.management_password = host["management_password"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        LOG.error(
            f"The host {host['hostname']} does not exist, when looking for management_password."
        )


def _update_connector(hosts, host):
    """Update the connector of the host.

    :param hosts: List of hosts
    :type hosts: list

    :param host: Host to update the connector
    :type host: dict
    """
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.connector = host["connector"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        LOG.error(
            f"The host {host['hostname']} does not exist, when looking for connector."
        )


def _update_hosts(hosts):
    """Update the hosts into the database.

    :param hosts: List of hosts
    :type hosts: list(BaseMachine)
    """
    for host in hosts:
        # Check if the host already exists in the database
        if _check_host_exists_by_hostname(host.hostname):
            _host_exists(host)
        else:
            _host_not_exists(host)

    # Update the pending hosts until the list is empty or there is no possible update
    possible_update = True
    while len(pending_hosts) > 0 and possible_update:
        for host in pending_hosts:
            # Check if there is not conflict with the IP of the host now
            repetedip_host = _check_host_exists_by_ip(host.management_ip)
            if not repetedip_host:
                _update_host(host)
                pending_hosts.remove(host)
                possible_update = True
            else:
                LOG.warning(
                    f"Host {host.hostname} was not updated because the ip {host.management_ip} already exists in the database in the host {repetedip_host.hostname}."
                )
                possible_update = False


def _host_exists(host):
    """Actions to perform if the host already exists in the database.

    :param host: Host to update
    :type host: BaseMachine
    """
    # Check if the host data has changed
    if _check_host_data_changed(host):
        # Check if the ip changed
        if _check_host_ip_changed(host):
            # Check the uniqueness of the ip of the new host
            repetedip_host = _check_host_exists_by_ip(host.management_ip)
            if repetedip_host:
                # Save the host in the pending_hosts list to update it later
                pending_hosts.append(host)
            else:  # Update the host
                _update_host(host)
        else:
            _update_host(host)
    else:
        LOG.debug(f"Host {host.hostname} is already up to date.")


def _host_not_exists(host):
    """Actions to perform if the host not exists in the database.

    :param host: Host to create
    :type host: BaseMachine
    """
    # Check the uniqueness of the ip of the new host
    repetedip_host = _check_host_exists_by_ip(host.management_ip)
    if repetedip_host:
        LOG.warning(
            f"Host {host.hostname} was not created because the ip {host.management_ip} already exists in the database in the host {repetedip_host.hostname}."
        )
    else:  # Create the host
        _create_host(host)


def _check_host_exists_by_hostname(hostname):
    """Check if the host already exists in the database by its hostname.

    :param hostname: Hostname of the host
    :type hostname: str

    :return: True if the host exists, False if the host does not exist
    :rtype: bool
    """
    db = next(get_db())
    return db.query(Machines).filter(Machines.hostname == hostname).first()


def _check_host_data_changed(host):
    """Check if the host data has changed.

    :param host: Host to check
    :type host: BaseMachine

    :return: True if the data has changed, False if the data has not changed
    :rtype: bool
    """
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host.hostname).first()

    if machine is None:
        return True  # Redundant but it is more clear (prevents errors)

    # If the host data is the same from the database, return False
    if (
        machine.groupname == host.groupname
        and machine.brand_model == host.brand_model
        and machine.management_ip == host.management_ip
        and machine.management_username == host.management_username
        and machine.management_password == host.management_password
        and machine.connector == host.connector
    ):
        return False
    else:
        return True


def _check_host_ip_changed(host):
    """Check if the host ip has changed.

    :param host: Host to check
    :type host: BaseMachine

    :return: True if the ip has changed, False if the ip has not changed
    :rtype: bool
    """
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host.hostname).first()

    if machine is None:
        return True  # Redundant but it is more clear (prevents errors)

    if machine.management_ip == host.management_ip:
        return False
    else:
        return True


def _check_host_exists_by_ip(management_ip):
    """Check if the host already exists in the database by its ip.

    :param management_ip: IP of the host
    :type management_ip: str

    :return: Host if it exists, None if it does not exist
    :rtype: MachineModel
    """
    db = next(get_db())
    return db.query(Machines).filter(Machines.management_ip == management_ip).first()


def _update_host(host):
    """Update the host in the database.

    :param host: Host to update
    :type host: BaseMachine
    """
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host.hostname).first()

    # Copy the new data to the host
    for key, value in host.dict().items():
        setattr(machine, key, value)

    db.commit()
    LOG.info(f"Host {host.hostname} updated successfully.")


def _create_host(host):
    """Create a host in the database.

    :param host: Host to create
    :type host: BaseMachine
    """
    db = next(get_db())
    new_machine_model = Machines()

    # Copy the new data from the host
    for key, value in host.dict().items():
        setattr(new_machine_model, key, value)

    db.add(new_machine_model)
    db.commit()
    LOG.info(f"Host {host.hostname} created successfully.")


def _update_available_machines(hosts):
    """Update the availability of the machines in the database.

    :param hosts: List of hosts
    :type hosts: List[BaseMachine]
    """
    # Obtain the list of machines from the database
    db = next(get_db())
    machines = db.query(Machines).all()

    # Disable the machines that are not in the hosts.yaml file using the hostname
    for machine in machines:
        if machine.hostname not in [host.hostname for host in hosts]:
            # If the machine is enabled, disable it
            if machine.available:
                machine.available = False
                # Also disable the monitoring flag of the machine (because it is not available)
                machine.monitoring = False
                db.commit()
                LOG.critical(f"Host {machine.hostname} is not available now.")
        else:
            # If the machine is disabled, enable it
            if not machine.available:
                machine.available = True
                db.commit()
                LOG.critical(f"Host {machine.hostname} is available now.")
