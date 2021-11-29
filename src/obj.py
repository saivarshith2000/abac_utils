# ABAC obj attribute client
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import os
import sys
import click
from pathlib import Path
from multiprocessing.connection import Client
from .config import PORT, SHARED_DIR

address = ('localhost', PORT)

def input_obj_avps(avps):
    while True:
        attr = input("Attribute: ")
        if not attr:
            break
        value = input("Value: ")
        if not value:
            break
        avp = f"{attr.lower().rstrip()}={value.lower().rstrip()}"
        if avp in avps:
            print(f"Attribute-Value pair {avp} already exists in the rule")
        else:
            avps.append(avp)
    if len(avps) == 0:
        print("Atleast one attribute-value pair is required. Aborted")
        sys.exit()
    return avps

def get_available_avps():
    payload = {"action": "AVAILABLE"}
    with Client(address) as conn:
        conn.send(payload)
        msg = conn.recv()
    if "error" in msg:
        sys.exit(f"The following error occured\n{msg['error']}")
    return msg["avps"]

def get_assigned_attr(object_path):
    uid = os.geteuid()
    payload = {"action": "LIST", "uid": uid, "object": object_path}
    with Client(address) as conn:
        conn.send(payload)
        msg = conn.recv()
    if "error" in msg:
        sys.exit(f"The following error occured\n{msg['error']}")
    avps = msg["avps"]
    return avps

def print_avps(avps, exit=False):
    if len(avps.keys()) == 0:
        if exit:
            sys.exit("No attributes assigned to this object.")
        else:
            print("No attributes assigned to this object.")
            return
    for i, (name, value)in enumerate(avps.items()):
        print(f"[{i}] {name} = {value}")

def list_attr(object_path):
    avps = get_assigned_attr(object_path)
    print_avps(avps)

def add_attr(object_path):
    available_avps = get_available_avps()
    if len(available_avps.keys()) == 0:
        print("No attributes avialable to assign to this object")
        sys.exit()

    assigned_avps = get_assigned_attr(object_path)
    print_avps(assigned_avps)
    valid_names = [n for n in available_avps.keys() if n not in assigned_avps.keys()]
    if len(valid_names) == 0:
        print("No more attributes available to assign")
        sys.exit()

    new_name = input(f"Select new attribute from - {', '.join(valid_names)}: ")
    if new_name not in valid_names:
        sys.exit("Invalid attribute name.")
    valid_values = available_avps[new_name]
    new_value = input(f"Select new value - {new_name} from [{', '.join(valid_values)}]: ")
    if new_value not in valid_values:
        sys.exit("Invalid attribute value.")
    assigned_avps[new_name] = new_value
    payload = {"action": "UPDATE", "object": object_path,"uid": os.geteuid(), "avps": assigned_avps}
    with Client(address) as conn:
        conn.send(payload)
        msg = conn.recv()
    if "error" in msg:
        sys.exit(f"The following error occured\n{msg['error']}")
    if "status" in msg and msg["status"] == "OK":
        print("Success")

def change_attr(object_path):
    available_avps = get_available_avps()
    assigned_avps = get_assigned_attr(object_path)
    print_avps(assigned_avps, exit=True)
    name = input(f"Select attribute to change - {', '.join(assigned_avps.keys())}: ")
    if name not in assigned_avps.keys():
        sys.exit("Invalid attribute name.")
    values = available_avps[name]
    val = input(f"Select new value for attribute - {name} from [{', '.join(values)}]: ")
    if val not in values:
        sys.exit("Invalid value")
    assigned_avps[name] = val
    payload = {"action": "UPDATE", "object": object_path,"uid": os.geteuid(), "avps": assigned_avps}
    with Client(address) as conn:
        conn.send(payload)
        msg = conn.recv()
    if "error" in msg:
        sys.exit(f"The following error occured\n{msg['error']}")
    if "status" in msg and msg["status"] == "OK":
        print("Success")


def delete_attr(object_path):
    assigned_avps = get_assigned_attr(object_path)
    print_avps(assigned_avps, exit=True)
    name = input(f"Select attribute to delete - {', '.join(assigned_avps.keys())}: ")
    if name not in assigned_avps.keys():
        sys.exit("Invalid attribute name.")
    del assigned_avps[name]
    payload = {"action": "UPDATE", "object": object_path,"uid": os.geteuid(), "avps": assigned_avps}
    with Client(address) as conn:
        conn.send(payload)
        msg = conn.recv()
    if "error" in msg:
        sys.exit(f"The following error occured\n{msg['error']}")
    if "status" in msg and msg["status"] == "OK":
        print("Success")


@click.command()
@click.argument('action', type=click.Choice(['list', 'add', 'delete', 'change']))
@click.argument('object_path', type=str)
def obj(action, object_path):
    """\b
    Set ABAC object attributes. Available actions
    list    - List the attributes of an object
    add     - Add attributes for an object
    change  - Change an object's attribute value
    delete  - Delete an existing object's attributes
    """

    object_path = str(Path(object_path).resolve())
    secured_dir_path = str(Path(SHARED_DIR))
    if object_path[:len(secured_dir_path)] != secured_dir_path:
        sys.exit(f"Only files in the {SHARED_DIR} are covered by ABAC rules")

    try:
        if action == "list":
            list_attr(object_path)
        elif action == "add":
            add_attr(object_path)
        elif action == "delete":
            delete_attr(object_path)
        elif action == "change":
            change_attr(object_path)
    except ConnectionError:
        sys.exit("Failed to connect to the ABAC object attribute service. Please make sure that it is running.")
    except Exception as e:
        print("The following occured\n", e)
        sys.exit(f"Connection closed unexpectedly")

if __name__ == "__main__":
    main()
