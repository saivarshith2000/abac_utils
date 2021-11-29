# ABAC user management
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import pwd
import os
import sys
import grp
from subprocess import Popen, PIPE
import getpass
import click
import crypt
import json
from pathlib import Path
from .load import load_user_attr
from .config import CONFIG_ROOT, CONFIG_USER_ATTRS_FILE, CONFIG_AVP_FILE
from .common import check_root, validate_str

user_attr_path = CONFIG_ROOT + CONFIG_USER_ATTRS_FILE
avp_path = CONFIG_ROOT + CONFIG_AVP_FILE 

def get_password():
    """
    Prompt user for password. Check that input is a valid password and return
    encrypted password for the useradd command
    """ 
    password = getpass.getpass("Password: ")
    confirm_pass = getpass.getpass("Re-enter Password: ")
    if password != confirm_pass:
        sys.exit("Invalid pasword") 
    else:
        return crypt.crypt(password,"22")

def verify_user_attr_initialized():
    if not Path(user_attr_path).is_file():
        sys.exit("ABAC config not initialized. user attributes file: {user_attr_path} missing")
    if not Path(avp_path).is_file():
        sys.exit("ABAC config not initialized. Attribute-Value file: {avp_path} missing")

def abac_group_created():
    # check if the 'abac' user group is created
    if not 'abac' in [g.gr_name for g in grp.getgrall()]:
        sys.exit("'abac' group not found. Please create this group before adding users. Users will be added to this group")


def user_attr_exists(username):
    with open(user_attr_path) as f:
        users = json.load(f)["users"]
        if username in users:
            return True
    return False

def add_user(username):
    """
    Attempts to add a new user into the system and populate the user attribute file
    """
    with open(avp_path) as f:
        available_avps = json.load(f)['user']
    if len(available_avps.keys()) == 0:
        sys.exit("User attribute value pairs not initialized.")
    if user_attr_exists(username):
        sys.exit(f"User {username} already exists in ABAC config.")
    # collect attribute value pairs
    print(f"Assign attributes to the new user {username}")
    print(f"Select a value for each attribute (ENTER to skip an attribute)")
    selected_avps = {}
    for name, values in available_avps.items():
        print(f"{name} : {', '.join(values)}")
        selected = input("value: ")
        if selected == "":
            continue
        if selected not in values:
            sys.exit("Invalid selection.")
        selected_avps[name] = selected
    if len(selected_avps) == 0:
        sys.exit("Atleast one attribute must be assigned")
    print()
    print(f"Creating user : {username} with following attribute-values")
    for name,value in selected_avps.items():
        print(f"{name} = {value}")
    print()
    try:
        print(f"Adding user {username} to the system")
        enc_password = get_password()
        p = Popen(["useradd", "-m" , "-G", "abac" ,"-p", enc_password, username], stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0: 
            sys.exit(f"failed to add user\nError\n{error.decode('utf-8')}")
        uid = pwd.getpwnam(username).pw_uid
        print(f"User {username}:{uid} added successfully")
        data = {}
        data['uid'] = uid
        data['avps'] = selected_avps
        with open(user_attr_path, 'r') as f:
            users = json.load(f)
            users['users'][username] = data
        with open(user_attr_path, 'w') as f:
            json.dump(users, f)
        print(f"User attributes written to config successfully.")
        load_user_attr()
    except Exception as e:
        print(e)
        print(f"Failed to add abac user.")
        sys.exit(1)

def manage_user(username):
    '''
    Modify user attributes
    '''
    with open(user_attr_path) as f:
        users = json.load(f)
        if username not in users["users"]:
            sys.exit(f"User {username} doesn't have any attributes")
        user = users['users'][username]
    with open(avp_path) as f:
        available_avps = json.load(f)['user']
    print(f"Attribute-Value pairs of user : {username}")
    for i, (name, value) in enumerate(user['avps'].items()):
        print(f"[{i}] {name} = {value}")
    msg = "Choose action: Add new attribute [A], delete existing attribute [D], Change value of attribute [C], Cancel [ENTER]: " 
    if len(user['avps'].keys()) == 0:
        msg = "Choose action: Add new attribute [A], Cancel [ENTER]: "
    action = input(msg)
    if action == "":
        return
    action = action.lower().strip()
    if action == "a":
        valid_names = [n for n in available_avps.keys() if n not in user['avps'].keys()]
        if len(valid_names) == 0:
            sys.exit("No more attributes to add")
        new_name = input(f"Select new attribute from : {', '.join(valid_names)}:   ")
        if new_name not in valid_names:
            sys.exit("Invalid attribute name.")
        valid_values = available_avps[new_name]
        new_value = input(f"Select new value from : {', '.join(valid_values)}:  ")
        if new_value not in valid_values:
            sys.exit("Invalid attribute value.")
        user['avps'][new_name] = new_value
    elif action == "c":
        name = input("Enter name of attribute to change: ")
        if name not in user['avps']:
            sys.exit("Invalid attribute name.")
        valid_values = available_avps[name]
        new_value = input(f"Select new value from : {', '.join(valid_values)}:  ")
        if new_value not in valid_values:
            sys.exit("Invalid attribute value.")
        user['avps'][name] = new_value
    elif action == "d":
        name = input("Enter name of attribute to delete: ")
        if name not in user['avps']:
            sys.exit("Invalid attribute name.")
        del user['avps'][name]
    users['users'][username] = user
    with open(user_attr_path, 'w') as f:
        json.dump(users, f)
    load_user_attr()
    print("Success")

def delete_user(username):
    '''
    Remove user and its attribute-value pairs from config
    '''
    # remove user from system
    confirm = input(f"Are you sure you want to remove user {username} from the system? [Y/N] ")
    if confirm.lower() != "y":
        sys.exit("Aborted")
    try:
        p = Popen(["deluser", "--remove-home" , username], stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0: 
            print(f"failed to delete user\nError\n{error.decode('utf-8')}")
            print("The user might have been deleted already using the 'deluser' command. Removing attribute data from config")
    except Exception as e:
        print(e)
        print(f"Failed to delete user {username}.")
    # delete user data from user_attrs
    with open(user_attr_path) as f:
        users = json.load(f)
        if username not in users["users"]:
            sys.exit(f"user {username} not found in config")
    del users["users"][username]
    with open(user_attr_path, 'w') as f:
        json.dump(users, f)
    print(f"user {username} deleted successfully\n")
    print("Reloading user attributes into the kernel")
    load_user_attr()

def list_users():
    '''
    List users and their attribute-value pairs 
    '''
    with open(user_attr_path) as f:
        users = json.load(f)["users"]
    for i, (username, userdata) in enumerate(users.items()):
        deleted = False
        try:
            uid_sys = pwd.getpwnam(username).pw_uid
        except KeyError:
            deleted = True
        avps = []
        for name, value in userdata['avps'].items():
            avps.append(f"{name} = {value}")
        uid = userdata['uid']
        print(f"[{i}] {username} : {uid} : {','.join(avps)} {'[user deleted from system]' if deleted else ''}")

@click.command()
@click.argument('action', type=click.Choice(['add', 'manage', 'list', 'delete']))
@click.argument('username', type=str, required=False)
def user(action, username):
    """\b
    Manage ABAC User attributes. YOU MUST BE ROOT TO USE THIS COMMAND

    The following actions are supported.
    add     - Create a new user and add attributes
    manage  - Mange an existing user's attributes
    list    - List abac users and their attributes
    delete  - Delete a user and corresponding attributes"""

    check_root()
    verify_user_attr_initialized()
    abac_group_created()

    if action == 'list':
        list_users()
    elif not validate_str(username):
        sys.exit("invalid username. Username must be an alpha numeric")
    elif action == 'add':
        add_user(username)
    elif action == 'manage':
        manage_user(username)
    elif action == 'delete':
        delete_user(username)
