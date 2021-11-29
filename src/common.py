# Common utility methods
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import os
import sys

def check_root():
    # check if user is root
    if os.geteuid() != 0:
        sys.exit("Only root can run this command. Try running with sudo or login as root.")

def validate_str(string):
    # valid string must be alphanumeric strings without spaces
    # this validation applies to usernames, attribute names and attribute values
    return string != None and string != "" and ' ' not in string and string.isalnum()
