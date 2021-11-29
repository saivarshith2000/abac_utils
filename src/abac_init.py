# ABAC policy and attribute store initialization
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import os
import sys
import click
import json
from pathlib import Path
from .config import *
from .common import check_root

def create_file(path, force, msg, content=None):
    # create file based on the force flag
    if Path(path).is_file():
        if force:
            open(path, 'w').close()
        else:
            print(msg)
            return
    else:
        open(path, 'w').close()
    if content:
        with open(path, 'w') as f:
            json.dump(content, f, indent=4)
    # chmod 660 = only root can read/write to this directory and its contents
    #os.chmod(CONFIG_ROOT, 0o660)

@click.command()
@click.option('-f', '--force', default=False, is_flag=True, help='Force initialize config. Overwrites existing policy and attributes.')
def init(force):
    """\b
    Initialize the ABAC config directory at /etc/abac/ and create the required files.
    These files can be accessed in any mode by root only. These file are mandatory for
    the ABAC system to work. The files are listed below:
    /etc/abac/                  - root config directory
    /etc/abac/user_attr.json    - ABAC User attributes
    /etc/abac/obj_attr          - ABAC Object attributes
    /etc/abac/policy            - ABAC Policy attributes
    /etc/abac/avp.json          - Valid Object attribute value pairs
    """
    check_root()

    if force:
        confirm = input("Are you sure you want to overwrite existing config ? It will remove all the existing ABAC attributes and rules [Y/N] ? ")
        if confirm.lower() != "y":
            sys.exit("Aborted")

    # create the abac config root directory
    if Path(CONFIG_ROOT).is_dir():
        print("ABAC Root config directory already exists")
    else:
        Path(CONFIG_ROOT).mkdir(parents=True, exist_ok=True)
        #chmod 660 = only root can read/write to this directory and its contents
        os.chmod(CONFIG_ROOT, 0o660)

    # create the user attributes file
    create_file(CONFIG_ROOT + CONFIG_USER_ATTRS_FILE, force, "User attributes file already exists", {"users": {}})

    # create the object attributes file
    create_file(CONFIG_ROOT + CONFIG_OBJ_ATTRS_FILE, force, "Object attributes file already exists", {"objects": {}})

    # create the kernel attributes file
    create_file(CONFIG_ROOT + CONFIG_ENV_ATTRS_FILE, force, "Environment attributes file already exists", {"env": {}})

    # create the policy file
    create_file(CONFIG_ROOT + CONFIG_POLICY_FILE, force, "ABAC Policy file already exists", {"rules": []})

    # create the object attributes-value pairs file
    avp = {
            "user": {}, 
            "obj": {}, 
            "env": {
                # currently hard coded
                "day": ["weekday", "weekend"],
                "time": ["working_hours", "after_hours"],
                }
            }
    create_file(CONFIG_ROOT + CONFIG_AVP_FILE, force, "ABAC Attribute Value pairs file already exists", avp)

    # check if the shared abac directory is created and leave a message to inform the admin
    if not Path(SHARED_DIR).is_dir():
        print(f"The ABAC shared directory - {SHARED_DIR} is NOT created. Files in this directory are the only ones covered by the abac policy")
    else:
        print(f"The ABAC shared directory - {SHARED_DIR} is created. Files in this directory are covered by the abac policy")

    print("Initialization successful")
