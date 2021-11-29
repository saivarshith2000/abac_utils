# ABAC load command for loading attributes and policy into kernel
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import os
import sys
import click
import json
from pathlib import Path
from .common import check_root
from .config import *

def check_files(config_path, kernel_path):
    """
    Checks if the files at config_path and kernel_paths are available.
    """
    if not Path(config_path).is_file():
            sys.exit(f"ABAC config not initialized. {config_path} missing")
    if not Path(kernel_path).is_file():
        sys.exit(f"Kernel User attribute file {kernel_path} not found.")

def load_user_attr():
    """parse user attributes json config and load them into the kernel"""
    # check if the user attributes file is present
    config_path = CONFIG_ROOT + CONFIG_USER_ATTRS_FILE  
    kernel_path = ABAC_MOUNT + KERN_USER_ATTRS_FILE  
    check_files(config_path, kernel_path)

    with open(config_path) as f:
        users = json.load(f)["users"]
    if len(users.keys()) == 0:
        print("No user attributes found. Not writing anything...")
        return
    content = ""
    for username, data in users.items():
        avps = []
        for name, value in data['avps'].items():
            avps.append(f"{name}={value}")
        if len(avps) == 0:
            continue
        content += f"{data['uid']}:{','.join(avps)}\n"
    with open(kernel_path, 'w') as f:
        f.write(content)
    print("User attributes loaded into the kernel")

def load_obj_attr():
    """parse user attributes json config and load them into the kernel"""
    # check if the user attributes file is present
    config_path = CONFIG_ROOT + CONFIG_OBJ_ATTRS_FILE
    kernel_path = ABAC_MOUNT + KERN_OBJ_ATTRS_FILE 
    check_files(config_path, kernel_path)

    # read object attributes, parse them and write data to kernel file
    with open(config_path) as f:
        objects = json.load(f)["objects"]
    if len(objects.keys()) == 0:
        print("No object attributes found. Not writing anything...")
        return
    content = ""
    for path, avp_dict in objects.items():
        avps = []
        for name, value in avp_dict.items():
            avps.append(f"{name}={value}")
        if len(avps) == 0:
            continue
        content += f"{path}:{','.join(avps)}\n"
    with open(kernel_path, 'w') as f:
        f.write(content)
    print("Object attributes loaded into the kernel")

def load_env_attr():
    """parse environment attributes json config and load them into the kernel"""
    # check if the user attributes file is present
    config_path = CONFIG_ROOT + CONFIG_ENV_ATTRS_FILE
    kernel_path = ABAC_MOUNT + KERN_ENV_ATTRS_FILE 
    check_files(config_path, kernel_path)

    # read object attributes, parse them and write data to kernel file
    with open(config_path) as f:
        envs = json.load(f)["env"]
    if len(envs.keys()) == 0:
        print("No Environment attributes found. Not writing anything...")
        return
    content = ""
    for env, value in envs.items():
        content += f"{env}={value}\n"
    with open(kernel_path, 'w') as f:
        f.write(content)
    print("Environment attributes loaded into the kernel")


def load_policy():
    """parse policy json and load the rules into the kernel"""
    config_path = CONFIG_ROOT + CONFIG_POLICY_FILE
    kernel_path = ABAC_MOUNT + KERN_POLICY_FILE
    check_files(config_path, kernel_path)

    # read object attributes, parse them and write data to kernel file
    with open(CONFIG_ROOT + CONFIG_POLICY_FILE) as f:
        rules = json.load(f)["rules"]
    if len(rules) == 0:
        print("No rules found. Not writing anything...")
        return
    content = ""
    for rule in rules:
        # user attrs
        avps = []
        for name, value in rule["user"].items():
            avps.append(f"{name}={value}")
        line = ",".join(avps) + "|"
        # obj attrs
        avps = []
        for name, value in rule["obj"].items():
            avps.append(f"{name}={value}")
        line += ",".join(avps) + "|"
        # env attrs
        avps = []
        for name, value in rule["env"].items():
            avps.append(f"{name}={value}")
        if len(avps) == 0:
            line += "*" + "|"
        else:
            line += ",".join(avps) + "|"
        line += rule["op"] + "\n"
        content += line
    with open(ABAC_MOUNT + KERN_POLICY_FILE, 'w') as f:
        f.write(content)
    print("ABAC Policy loaded into kernel")

@click.command()
def load():
    """Load user, object attributes and ABAC Policy into the Kernel"""

    check_root()

    # check if the ABAC LSM's Security File System is initialized. If it was,
    # it is mounted at ABAC_MOUNT. If it wasn't, throw an error with some info.
    p = Path(ABAC_MOUNT)
    if not p.is_dir():
        sys.exit(f"ABAC security file system is not mounted. Please check if the ABAC LSM is loaded")

    load_policy()
    load_user_attr()
    load_obj_attr()
    load_env_attr()
