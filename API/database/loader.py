import ipaddress

import yaml
from database.config import create_tables, get_db
from log import logger
from models.machine import Machines
from schemas.machine import BaseMachine
from yaml.loader import SafeLoader

FILE = "../CPD.yaml"

pending_hosts = []  # List of hosts not updated because the ip already exists previously


# Load the initial data .yaml file
def load_hosts():
    logger.info("Loading the hosts.yaml file into the database.")

    # Create the tables in the database
    create_tables()

    # Obtain the list of groups from the file
    group_list = read_groups()

    # Convert the list of groups to a list of hosts (BaseMachine objects)
    hosts_list = convert_groups_to_hosts(group_list)

    # Update the database table with the hosts from the hosts.yaml file
    update_hosts(hosts_list)

    # Update the available machines in the database
    update_available_machines(hosts_list)

    logger.info("The hosts.yaml file has been loaded into the database.")


# Read the file:
def read_groups():
    with open(FILE, "r") as stream:
        try:
            groups = yaml.load(stream, Loader=SafeLoader)
            return groups
        except yaml.YAMLError as exc:
            print(exc)


# Convert the list of groups to a list of machines (BaseMachine)
def convert_groups_to_hosts(groups):
    # List of hosts obtained from the groups
    hosts_obtained_from_group = []

    # For each group, create a list of hosts
    for group in groups:
        new_group_list = create_hosts_list(group)

        # Add particular hosts atributtes to each host
        if "hosts" in group:  # If the group has particular hosts
            for host in group["hosts"]:  # For each particular host
                find_particular_atributtes(new_group_list, host)

        # If the group has been created correctly, add it to the list of groups (Not empty)
        if new_group_list:
            hosts_obtained_from_group.append(new_group_list)

    # Flatten the list of lists of hosts to a list of hosts
    hosts_obtained_from_group = [
        host for sublist in hosts_obtained_from_group for host in sublist
    ]

    return hosts_obtained_from_group


# Aux functions to parse the initial data .yaml file


# Create a list of hosts from a group
def create_hosts_list(group):
    # Check for consistency of the hostname and the groupname
    if not check_hostname_consistency(group):
        return []  # Return an empty list

    # Check that the number of hosts is equal to the number of IPs
    if not check_number_of_hosts_and_ips(group):
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
            logger.error(
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
                monitoring=False,  # By default, the machine is unmonitored
                available=True,  # By default, the machine is available
            )
            new_hosts_list.append(host)
            first_ip += 1

    return new_hosts_list


# Check if the hostname is consistent with the groupname
def check_hostname_consistency(group):
    if (group["hostname_range"][0])[: len(group["groupname"])] != group["groupname"]:
        logger.error(
            f"The hostname of the group {group['groupname']} is not consistent with the groupname."
        )
        return False
    else:
        return True


# Check if the number of hosts is equal to the number of IPs
def check_number_of_hosts_and_ips(group):
    # If there is only one host, check that there is only one IP
    if len(group["hostname_range"]) == 1 and len(group["management_ip_range"]) != 1:
        logger.error(
            f"The group {group['groupname']} has only one host but more than one IP."
        )
        return False

    # If there is only one IP, check that there is only one host
    if len(group["hostname_range"]) != 1 and len(group["management_ip_range"]) == 1:
        logger.error(
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
        logger.error(
            f"The number of hosts of the group {group['groupname']} is not equal to the number of IPs."
        )
        return False
    else:
        return True


# Find the particular atributtes of a host and add them to the host
def find_particular_atributtes(hosts, host):
    # If the host has a particular brand_model, add it to the host
    if "brand_model" in host:
        update_brand_model(hosts, host)
    # If the host has a particular management_ip, add it to the host
    if "management_ip" in host:
        update_management_ip(hosts, host)
    # If the host has a particular management_username, add it to the host
    if "management_username" in host:
        update_management_username(hosts, host)
    # If the host has a particular management_password, add it to the host
    if "management_password" in host:
        update_management_password(hosts, host)


# Update the brand_model of the host
def update_brand_model(hosts, host):
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.brand_model = host["brand_model"]
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        logger.error(
            f"The host {host['hostname']} does not exist, when looking for brand_model."
        )


# Update the management_ip of the host
def update_management_ip(hosts, host):
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.management_ip = host["management_ip"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        logger.error(
            f"The host {host['hostname']} does not exist, when looking for management_ip."
        )


# Update the management_password of the host
def update_management_username(hosts, host):
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.management_username = host["management_username"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        logger.error(
            f"The host {host['hostname']} does not exist, when looking for management_username."
        )


# Update the management_password of the host
def update_management_password(hosts, host):
    found = False
    for h in hosts:
        if h.hostname == host["hostname"]:
            h.management_password = host["management_password"]
            found = True
            break
    # If the host does not exist, notify it in the log because it is a mistake
    if not found:
        logger.error(
            f"The host {host['hostname']} does not exist, when looking for management_password."
        )


# Update the hosts into the database
def update_hosts(hosts):
    for host in hosts:
        # Check if the host already exists in the database
        if check_host_exists_by_hostname(host.hostname):
            host_exists(host)
        else:
            host_not_exists(host)

    # Update the pending hosts until the list is empty or there is no possible update
    possible_update = True
    while len(pending_hosts) > 0 and possible_update:
        for host in pending_hosts:
            # Check if there is not conflict with the IP of the host now
            if not check_host_exists_by_ip(host.management_ip):
                update_host(host)
                pending_hosts.remove(host)
                possible_update = True
            else:
                possible_update = False


# Actions to perform if the host already exists in the database
def host_exists(host):
    # Check if the host data has changed
    if check_host_data_changed(host):
        # Check if the ip changed
        if check_host_ip_changed(host):
            # Check the uniqueness of the ip of the new host
            repetedip_host = check_host_exists_by_ip(host.management_ip)
            if repetedip_host:
                logger.warning(
                    f"Host {host.hostname} was not updated because the ip {host.management_ip} already exists in the database in the host {repetedip_host.hostname}."
                )
                # Save the host in the pending_hosts list to update it later
                pending_hosts.append(host)
            else:  # Update the host
                update_host(host)
        else:
            update_host(host)
    else:
        logger.debug(f"Host {host.hostname} is already up to date.")


# Actions to perform if the host not exists in the database
def host_not_exists(host):
    # Check the uniqueness of the ip of the new host
    repetedip_host = check_host_exists_by_ip(host.management_ip)
    if repetedip_host:
        logger.warning(
            f"Host {host.hostname} was not created because the ip {host.management_ip} already exists in the database in the host {repetedip_host.hostname}."
        )
    else:  # Create the host
        create_host(host)


# Check if the host already exists in the database by its hostname
def check_host_exists_by_hostname(hostname):
    db = next(get_db())
    return db.query(Machines).filter(Machines.hostname == hostname).first()


# Check if the host data has changed
def check_host_data_changed(host):
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host.hostname).first()

    # If the host data is the same from the database, return False
    if (
        machine.groupname == host.groupname
        and machine.brand_model == host.brand_model
        and machine.management_ip == host.management_ip
        and machine.management_username == host.management_username
        and machine.management_password == host.management_password
    ):
        return False
    else:
        return True


# Check if the IP changed for the host
def check_host_ip_changed(host):
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host.hostname).first()
    if machine.management_ip == host.management_ip:
        return False
    else:
        return True


# Check if the host already exists in the database by its ip
def check_host_exists_by_ip(management_ip):
    db = next(get_db())
    return db.query(Machines).filter(Machines.management_ip == management_ip).first()


# Update the host in the database
def update_host(host):
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host.hostname).first()

    # Copy the new data to the host
    for key, value in host.dict().items():
        setattr(machine, key, value)

    db.commit()
    logger.debug(f"Host {host.hostname} updated successfully.")


# Create a host in the database
def create_host(host):
    db = next(get_db())
    new_machine_model = Machines()

    # Copy the new data from the host
    for key, value in host.dict().items():
        setattr(new_machine_model, key, value)

    db.add(new_machine_model)
    db.commit()
    logger.debug(f"Host {host.hostname} created successfully.")


# Disable the machines in the database that are not in the initial data .yaml file
# and enable the machines that are in the initial data .yaml file
def update_available_machines(hosts):
    # Obtain the list of machines from the database
    db = next(get_db())
    machines = db.query(Machines).all()

    # Disable the machines that are not in the hosts.yaml file using the hostname
    for machine in machines:
        if machine.hostname not in [host.hostname for host in hosts]:
            # If the machine is enabled, disable it
            if machine.available:
                machine.available = False
                db.commit()
                logger.critical(f"Host {machine.hostname} is not available now.")
        else:
            # If the machine is disabled, enable it
            if not machine.available:
                machine.available = True
                db.commit()
                logger.critical(f"Host {machine.hostname} is available now.")
