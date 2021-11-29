# Entrypoint for the ABAC command line tool
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

"""
Entrypoint for the abac userspace command line tool
"""
import click

from .abac_init import init
from .load import load
from .user import user
from .obj import obj
from .policy import policy
from .avp import avp
from .server import server
from .watch import watch
from .env_update import env_update

@click.group()
def main():
    "Manage ABAC attributes, values and entities."
    pass

main.add_command(init)
main.add_command(load)
main.add_command(user)
main.add_command(obj)
main.add_command(avp)
main.add_command(policy)
main.add_command(server)
main.add_command(watch)
main.add_command(env_update)
