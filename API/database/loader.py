import ipaddress

import yaml
from database.config import create_tables, get_db
from log import logger
from models.machine import Machines
from schemas.machine import BaseMachine
from yaml.loader import SafeLoader

FILE = "../CPD.yaml"

hosts = []  # List of hosts (BaseMachine objects)
pending_hosts = []  # List of hosts not updated because the ip already exists previously


# Load the hosts.yaml file
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
    for group in groups:
        for host in group["hosts"]:
            # Create a new machine object
            new_machine = BaseMachine(
                groupname=set_groupname(host, group),
                hostname=set_hostname(host),
                brand_model=set_brand_model(host, group),
                management_ip=set_management_ip(host, group),
                management_username=set_management_username(host, group),
                management_password=set_management_password(host, group),
                monitoring=False,  # By default, the machine is unmonitored
                available=True,  # By default, the machine is available
            )
            hosts.append(new_machine)
    return hosts


# Aux functions to parse the hosts.yaml file


# Set the groupname:
def set_groupname(host, group):
    # If the groupname is not defined in the host, set the groupname of the group
    if "groupname" not in host and "groupname" in group:
        host["groupname"] = group["groupname"]
    elif "groupname" not in host and "groupname" not in group:
        logger.error(
            f"The groupname is not defined in the group {group['groupname']}, neither the groupname in the host {host['hostname']}."
        )
    return group["groupname"]


# Set the hostname:
def set_hostname(host):
    return host["hostname"]


# Set the brand_model:
def set_brand_model(host, group):
    # If the brand_model is not defined in the host, set the brand_model of the group
    if "brand_model" not in host and "brand_model" in group:
        host["brand_model"] = group["brand_model"]
    elif "brand_model" not in host and "brand_model" not in group:
        logger.error(
            f"The brand_model is not defined in the group {group['groupname']}, neither the brand_model in the host {host['hostname']}."
        )
        exit(1)
    return host["brand_model"]


# Set the management_ip:
def set_management_ip(host, group):
    # If the management_ip is not defined in the host, set the an IP from the range of the group
    if "management_ip" not in host and "management_ip_range" in group:
        host["management_ip"] = get_next_ip_from_range(group)
    elif "management_ip" not in host and "management_ip_range" not in group:
        logger.error(
            f"The management_ip_range is not defined in the group {group['groupname']}, neither the management_ip in the host {host['hostname']}."
        )
        exit(1)
    return host["management_ip"]


# Get the next IP from the range of the group
def get_next_ip_from_range(group):
    # Get the first IP of the range
    start_ip = ipaddress.IPv4Address(group["management_ip_range"][0])
    # Get the last IP of the range
    end_ip = ipaddress.IPv4Address(group["management_ip_range"][1])

    next_ip = start_ip

    # Get the next IP of the last IP used in the group
    for host in hosts:
        if (
            host.groupname == group["groupname"]  # Same group
            and ipaddress.IPv4Address(host.management_ip) >= start_ip  # Same range
            and ipaddress.IPv4Address(host.management_ip) <= end_ip  # Same range
        ):
            next_ip = ipaddress.IPv4Address(host.management_ip) + 1

    # Check if the next IP is out of the range
    if next_ip > end_ip:
        logger.error(
            f"The range of the group {group['groupname']} is full. The IP {next_ip} is out of the range."
        )
        exit(1)
    return str(next_ip)


# Set the management_username:
def set_management_username(host, group):
    # If the management_username is not defined in the host, set the management_username of the group
    if "management_username" not in host and "management_username" in group:
        host["management_username"] = group["management_username"]
    elif "management_username" not in host and "management_username" not in group:
        logger.error(
            f"The management_username is not defined in the group {group['groupname']}, neither the management_username in the host {host['hostname']}."
        )
        exit(1)
    return host["management_username"]


def set_management_password(host, group):
    # If the management_password is not defined in the host, set the management_password of the group
    if "management_password" not in host:
        host["management_password"] = group["management_password"]
    elif "management_password" not in host and "management_password" not in group:
        logger.error(
            f"The management_password is not defined in the group {group['groupname']}, neither the management_password in the host {host['hostname']}."
        )
        exit(1)
    return host["management_password"]


# Update the hosts into the database
def update_hosts(hosts):
    for host in hosts:
        # Check if the host already exists in the database
        if check_host_exists_by_hostname(host.hostname):
            host_exists(host)
        else:
            host_not_exists(host)

    # Update the pending hosts until the list is empty
    while len(pending_hosts) > 0:
        for host in pending_hosts:
            if not check_host_exists_by_ip(host.management_ip):
                update_host(host)
                pending_hosts.remove(host)


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


# Disable the machines in the database that are not in the hosts.yaml file and enable the machines that are in the hosts.yaml file
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
