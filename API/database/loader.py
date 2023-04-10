import yaml
from database.config import create_tables, get_db
from log import logger
from models.machine import Machines
from yaml.loader import SafeLoader

FILE = "../CPD.yaml"

pending_hosts = []  # List of hosts not updated because the ip already exists previously


# Load the hosts.yaml file
def load_hosts():
    logger.info("Loading the hosts.yaml file into the database.")

    # Obtain the list of groups from the file
    group_list = read_groups()

    # Convert the list of groups to a list of hosts (dictionaries)
    hosts = convert_groups_to_hosts(group_list)

    # Create the tables in the database
    create_tables()

    # Update the database table with the hosts from the hosts.yaml file
    update_hosts(hosts)

    # Update the available machines in the database
    update_available_machines(hosts)

    logger.info("The hosts.yaml file has been loaded into the database.")


# Read the file:
def read_groups():
    with open(FILE, "r") as stream:
        try:
            groups = yaml.load(stream, Loader=SafeLoader)
            return groups
        except yaml.YAMLError as exc:
            print(exc)


# Convert the list of groups to a list of hosts (dictionaries)
def convert_groups_to_hosts(groups):
    hosts = []
    for group in groups:
        for host in group["hosts"]:
            host["groupname"] = group["groupname"]
            host["model"] = group["model"]
            hosts.append(host)
    return hosts


# Update the hosts into the database
def update_hosts(hosts):
    for host in hosts:
        # Check if the host already exists in the database
        if check_host_exists(host["hostname"]):
            host_exists(host)
        else:
            host_not_exists(host)


# Actions to perform if the host already exists in the database
def host_exists(host):
    # Check if the host data has changed
    if check_host_data_changed(host):
        # Check if the ip changed
        if check_host_ip_changed(host):
            # Check the uniqueness of the ip of the new host
            repetedip_host = check_host_exists_by_ip(host["ip"])
            if repetedip_host:
                logger.warning(
                    f"Host {host['hostname']} was not updated because the ip {host['ip']} already exists in the database in the host {repetedip_host.hostname}."
                )
                # Save the host in the pending_hosts list to update it later
                pending_hosts.append(host)
            else:  # Update the host
                update_host(host)
        else:
            update_host(host)
    else:
        logger.debug(f"Host {host['hostname']} is already up to date.")

    # Check if there are hosts in the pending_hosts list (not updated because the ip already exists previously)
    if pending_hosts:
        for host in pending_hosts:
            if not check_host_exists_by_ip(host["ip"]):
                update_host(host)
                pending_hosts.remove(host)


# Actions to perform if the host not exists in the database
def host_not_exists(host):
    # Check the uniqueness of the ip of the new host
    repetedip_host = check_host_exists_by_ip(host["ip"])
    if repetedip_host:
        logger.warning(
            f"Host {host['hostname']} was not created because the ip {host['ip']} already exists in the database in the host {repetedip_host.hostname}."
        )
    else:  # Create the host
        create_host(host)


# Check if the host already exists in the database by its hostname
def check_host_exists(hostname):
    db = next(get_db())
    return db.query(Machines).filter(Machines.hostname == hostname).first()


# Check if the host data has changed
def check_host_data_changed(host):
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host["hostname"]).first()
    if (
        machine.groupname == host["groupname"]
        and machine.model == host["model"]
        and machine.ip == host["ip"]
        and machine.username == host["username"]
        and machine.password == host["password"]
    ):
        return False
    else:
        return True


# Check if the IP changed for the host
def check_host_ip_changed(host):
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host["hostname"]).first()
    if machine.ip == host["ip"]:
        return False
    else:
        return True


# Check if the host already exists in the database by its ip
def check_host_exists_by_ip(ip):
    db = next(get_db())
    return db.query(Machines).filter(Machines.ip == ip).first()


# Update the host in the database
def update_host(host):
    db = next(get_db())
    machine = db.query(Machines).filter(Machines.hostname == host["hostname"]).first()

    # Copy the new data to the host
    machine.groupname = host["groupname"]
    machine.model = host["model"]
    machine.ip = host["ip"]
    machine.username = host["username"]
    machine.password = host["password"]

    db.commit()
    logger.debug(f"Host {host['hostname']} updated successfully.")


# Create a host in the database
def create_host(host):
    db = next(get_db())
    machine = Machines(
        groupname=host["groupname"],
        hostname=host["hostname"],
        model=host["model"],
        ip=host["ip"],
        username=host["username"],
        password=host["password"],
    )
    db.add(machine)
    db.commit()
    logger.debug(f"Host {host['hostname']} created successfully.")


# Disable the machines in the database that are not in the hosts.yaml file and enable the machines that are in the hosts.yaml file
def update_available_machines(hosts):
    # Obtain the list of machines from the database
    db = next(get_db())
    machines = db.query(Machines).all()

    # Disable the machines that are not in the hosts.yaml file using the hostname
    for machine in machines:
        if machine.hostname not in [host["hostname"] for host in hosts]:
            # If the machine is enabled, disable it
            if machine.available:
                machine.available = False
                db.commit()
                logger.critical(f"Host {machine.hostname} disabled successfully.")
        else:
            # If the machine is disabled, enable it
            if not machine.available:
                machine.available = True
                db.commit()
                logger.critical(f"Host {machine.hostname} enabled successfully.")
