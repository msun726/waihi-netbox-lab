import os
import requests
import csv
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Accept": "application/json",
}


def get_netbox_data(endpoint):
    """Get data from a NetBox API endpoint."""
    url = f"{NETBOX_URL}/api/{endpoint}/"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
        return response.json()["results"]

    except requests.exceptions.RequestException as error:
        print(f"API request failed: {error}")
        return []




devices = get_netbox_data("dcim/devices")

print("\n=== WAIHI MINING LAB DEVICE REPORT ===")

for device in devices:
    print(f"\nDevice: {device['name']}")
    print(f"Role: {device['role']['name']}")
    print(f"Status: {device['status']['label']}")
    print(f"Device Type: {device['device_type']['model']}")

print("\n=== INTERFACE REPORT ===")

interfaces = get_netbox_data("dcim/interfaces")

for interface in interfaces:
    device_name = interface["device"]["name"]
    interface_name = interface["name"]
    interface_type = interface["type"]["label"]

    mode = interface.get("mode")
    mode_label = mode["label"] if mode else "None"

    untagged_vlan = interface.get("untagged_vlan")
    if untagged_vlan:
        untagged = f"{untagged_vlan['vid']} {untagged_vlan['name']}"
    else:
        untagged = "-"

    tagged_vlans = interface.get("tagged_vlans", [])
    if tagged_vlans:
        tagged = ", ".join(
            f"{vlan['vid']} {vlan['name']}"
            for vlan in tagged_vlans
        )
    else:
        tagged = "-"

    print(
        f"{device_name} | {interface_name} | {interface_type} | "
        f"Mode: {mode_label} | Untagged: {untagged} | Tagged: {tagged}"
    )


print("\n=== VLAN REPORT ===")

vlans = get_netbox_data("ipam/vlans")

for vlan in vlans:
    print(f"VLAN {vlan['vid']} | {vlan['name']}")



print("\n=== IP ADDRESS REPORT ===")

ip_addresses = get_netbox_data("ipam/ip-addresses")

for ip in ip_addresses:
    address = ip["address"]
    dns_name = ip["dns_name"] or "-"

    assigned_object = ip.get("assigned_object")

    if assigned_object:
        interface_name = assigned_object.get("name", "-")
        device = assigned_object.get("device")
        device_name = device["name"] if device else "-"
    else:
        interface_name = "-"
        device_name = "-"

    print(
        f"{device_name} | {interface_name} | "
        f"{address} | DNS: {dns_name}"
    )


with open("devices.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Device Name",
        "Role",
        "Status",
        "Device Type"
    ])

    for device in devices:
        writer.writerow([
            device["name"],
            device["role"]["name"],
            device["status"]["label"],
            device["device_type"]["model"]
        ])

print("\nDevice inventory exported to devices.csv")

with open("network_inventory.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Device",
        "Interface",
        "Interface Type",
        "Mode",
        "Untagged VLAN",
        "Tagged VLANs"
    ])

    for interface in interfaces:
        device_name = interface["device"]["name"]
        interface_name = interface["name"]
        interface_type = interface["type"]["label"]

        mode = interface.get("mode")
        mode_label = mode["label"] if mode else "None"

        untagged_vlan = interface.get("untagged_vlan")
        if untagged_vlan:
            untagged = f"{untagged_vlan['vid']} {untagged_vlan['name']}"
        else:
            untagged = "-"

        tagged_vlans = interface.get("tagged_vlans", [])
        if tagged_vlans:
            tagged = ", ".join(
                f"{vlan['vid']} {vlan['name']}"
                for vlan in tagged_vlans
            )
        else:
            tagged = "-"

        writer.writerow([
            device_name,
            interface_name,
            interface_type,
            mode_label,
            untagged,
            tagged
        ])

print("Network inventory exported to network_inventory.csv")