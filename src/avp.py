# ABAC attribute-value pair management
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import json
import click
import sys
from pathlib import Path
from .common import check_root, validate_str
from .config import CONFIG_ROOT, CONFIG_AVP_FILE

avp_path = CONFIG_ROOT + CONFIG_AVP_FILE 

def check_avp():
    if not Path(avp_path).is_file():
        sys.exit(f"ABAC config not initialized. {avp_path} missing")

def print_avps(avps):
    if len(avps.keys()) == 0:
        return
    for i, (name, values) in enumerate(avps.items()):
        print(f"[{i}] {name}: {', '.join(values)}")

def add_attr(type_):
    with open(avp_path) as f:
        data = json.load(f)
    print_avps(data[type_])
    name = input("Enter new attribute name: ")
    if not validate_str(name):
        sys.exit("Invalid attribute name. Attribute name must be alpha numeric")
    if name in data[type_]:
        sys.exit(f"Attribute {name} already exists")
    values_input = input("Enter comma(',') values: ").strip()
    if values_input == "":
        sys.exit("Atleast one value is required")
    values = []
    for value in values_input.split(","):
        value = value.strip().lower() 
        if not validate_str(value):
            sys.exit("One of the values is invalid. Values must be alpha numeric")
        values.append(value)
    data[type_][name] = values
    with open(avp_path, 'w') as f:
        json.dump(data, f)
    print(f"New attribute-value pair {name}:{', '.join(values)} added successfully")

def list_attr(type_):
    with open(avp_path) as f:
        if type_:
            avps = json.load(f)[type_]
            print_avps(avps)
        else:
            avps = json.load(f)
            print("User Attribute-value pairs\n")
            print_avps(avps["user"])
            print("\nObject Attribute-value pairs\n")
            print_avps(avps["obj"])
            print("\nEnvironment Attribute-value pairs\n")
            print_avps(avps["env"])
            print()

def modify_attr(type_):
    with open(avp_path) as f:
        data = json.load(f)
    print_avps(data[type_])
    name = input("Name of the attribute to modify: ")
    if name not in data[type_]:
        sys.exit(f"attribute {name} not found")
    values = data[type_][name] 
    values_input = input("Enter new comma(',') values: ").strip()
    if values_input == "":
        sys.exit("Atleast one value is required")
    values = []
    for value in values_input.split(","):
        value = value.strip().lower() 
        if not validate_str(value):
            sys.exit("One of the values is invalid. Values must be alpha numeric")
        values.append(value)
    data[type_][name] = values
    with open(avp_path, 'w') as f:
        json.dump(data, f)
    print(f"Attribute-value pair {name}:{', '.join(values)} modified successfully")


def delete_attr(type_):
    with open(avp_path) as f:
        data = json.load(f)
    print_avps(data[type_])
    name = input("Name of the attribute-value pair to delete: ")
    if name not in data[type_]:
        sys.exit(f"attribute {name} not found")
    values = data[type_][name]
    del data[type_][name]
    with open(avp_path, 'w') as f:
        json.dump(data, f)
    print(f"attribute-value pair {name}:{','.join(values)} deleted successfully")

@click.command()
@click.option('-t', 'type_', type=click.Choice(['user', 'obj', 'env']), help="Type of the entity")
@click.argument('action', type=click.Choice(['add', 'list', 'delete', 'modify']))
def avp(action, type_):
    """\b
    Manage User and Object attribute-value pairs. 
    YOU MUST BE ROOT TO USE THIS ACTIONS OTHER THAN 'list'.
    The following actions are supported.
    add     - Add a new attribute and its possible values
    list    - List existing attribute-value pairs
    modify  - Modify the values of an existing attribute
    delete  - Delete an attribute-value pair"""

    check_root()
    check_avp()

    if action == "list":
        list_attr(type_)
    elif type_ is None:
        sys.exit("Entity type flag '-t' is required")
    elif type_ == "env":
        sys.exit("Environment attribute value pairs can't be modified")
    if action == "add":
        add_attr(type_)
    elif action == "modify":
        modify_attr(type_)
    elif action == "delete":
        delete_attr(type_)
