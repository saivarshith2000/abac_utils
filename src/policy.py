# ABAC policy management
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import os
import sys
import json
import click
from pathlib import Path
from .config import CONFIG_ROOT, CONFIG_POLICY_FILE, CONFIG_AVP_FILE
from .common import check_root
from .load import load_policy

policy_path = CONFIG_ROOT + CONFIG_POLICY_FILE
avp_path = CONFIG_ROOT + CONFIG_AVP_FILE

def check_policy_initialized():
    if not Path(policy_path).is_file():
        sys.exit("ABAC config not initialized. Policy file: {policy_path} missing")
    if not Path(avp_path).is_file():
        sys.exit("ABAC config not initialized. Attribute-Value file: {avp_path} missing")

def input_avps(header, available_avps, allow_empty=False):
    avps = {}
    print(header)
    for attr in available_avps.keys():
        val = input(f"Select the value for attribute  - {attr} from [{', '.join(available_avps[attr])}] : ")
        if not val or val == "":
            break
        if val not in available_avps[attr]:
            sys.exit("Invalid value")
        avps[attr] = val
    if len(avps.keys()) == 0 and not allow_empty:
        sys.exit("Atleast one attribute-value pair is required. Aborted")
    return avps

def print_rule(rule):
    user_avps = []
    for name, value in rule["user"].items():
        user_avps.append(f"{name}={value}")
    obj_avps = []
    for name, value in rule["obj"].items():
        obj_avps.append(f"{name}={value}")
    env_avps = []
    for name, value in rule["env"].items():
        env_avps.append(f"{name}={value}")
    # print * if not environment attribute are present in the rule
    return f"{' ^ '.join(user_avps)} | {' ^ '.join(obj_avps)} | {' ^ '.join(env_avps) if len(env_avps) != 0 else '*'} |{rule['op']}"


def list_rules():
    with open(policy_path, 'r') as f:
        rules = json.load(f)["rules"]
    if len(rules) == 0:
        print("No rules created yet")
        return
    for i, rule in enumerate(rules):
        print(f"[{i}] {print_rule(rule)}")

def add_rule():
    with open(policy_path, 'r') as f:
        rules = json.load(f)["rules"]
    with open(avp_path, 'r') as f:
        available_avps = json.load(f)
        if len(available_avps["user"].keys()) == 0:
            sys.exit("User attribute-value pairs are not yet created. Please create atleast one avp before adding rules.")
        if len(available_avps["obj"].keys()) == 0:
            sys.exit("Object attribute-value pairs are not yet created. Please create atleast one avp before adding rules.")

    print("Follow the prompt to add new rule")
    user_avps = input_avps("Input USER attribute-value pairs. Press ENTER to move to next step", available_avps["user"])
    obj_avps = input_avps("Input OBJECT attribute-value pairs. Press ENTER to move to next step", available_avps["obj"])
    env_avps = input_avps("Input Environment attribute-value pairs. Press ENTER to move to next step", available_avps["env"], allow_empty = True)
    op = input("Operation: Modify [M] or Read [R]: ")
    if not op:
        sys.exit()
    if op != "M" and op != "R":
        print("Invalid input")
        sys.exit()
    # build the final rule and check if it already exists in the policy
    new_rule = {'user': user_avps, 'obj': obj_avps, 'env': env_avps, 'op': "MODIFY" if op == "M" else "READ"}
    if new_rule in rules:
        sys.exit(f"{print_rule(new_rule)}\nRule already exists")
    confirm = input(f"{print_rule(new_rule)}\nAre you sure you want to add the above rule to the policy? [Y/N] ")
    if confirm.lower() != "y":
        sys.exit("Aborted")
    rules.append(new_rule)
    with open(policy_path, 'w') as f:
        json.dump({"rules": rules}, f)
    print("Rule added succesfully")
    load_policy()

def delete_rule():
    with open(policy_path, 'r') as f:
        rules = json.load(f)["rules"]
    if len(rules) == 0:
        print("No rules created yet")
        return

    for i, rule in enumerate(rules):
        print(f"[{i}] {print_rule(rule)}")
    index = input("Index of the rule to delete: ")
    if not index.isnumeric() or int(index) < 0 or int(index) >= len(rules):
        sys.exit("Invalid input")
    index = int(index)
    confirm = input(f"{print_rule(new_rule)}\nAre you sure you want to delete the above rule from the policy? [Y/N] ")
    if confirm.lower() != "y":
        sys.exit("Aborted")
    del(rules[index])
    with open(policy_path, 'w') as f:
        json.dump({"rules": rules}, f)
    print("Rule deleted successfully")
    load_policy()

@click.command()
@click.option('-f', '--force', default=False, is_flag=True, help='Force initialize policy file. Overwrites existing rules.')
@click.argument('action', type=click.Choice(['add', 'list', 'delete']))
def policy(action, force):
    """\b
    Manage ABAC Policy. YOU MUST BE ROOT TO USE THIS COMMAND
    The following actions are supported.
    add     - Add a new rule to the policy 
    list    - List existing rules in the policy
    delete  - Delete a rule from the policy"""

    check_root()
    check_policy_initialized()

    if action == "add":
        add_rule()
    elif action == "list":
        list_rules()
    elif action == "delete":
        delete_rule()
