# ABAC environmental attribute service
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import json
import time
import datetime
import click
from apscheduler.schedulers.blocking import BlockingScheduler
from .config import CONFIG_ROOT, CONFIG_ENV_ATTRS_FILE
from .common import check_root
from .load import load_env_attr

def update_day_env():
    """
    Gets the current day of week. Returns 'weekday' for Mon to Fri
    and 'weekend' for Sat and Sun
    """
    if datetime.date.today().strftime('%A') in ['Saturday', 'Sunday']:
        return 'weekend'
    return 'weekday'

def update_time_env():
    """
    Gets the current time of day. Returns 'working_hours' if time is between
    8:00 to 18:00 and 'after_hours' otherwise
    """
    h = datetime.datetime.now().hour  
    if h >= 8 and h <= 18:
        return 'working_hours'
    return 'after_hours'

def update_env(force=False):
    """
    Update the environment attributes file based on the current values.
    This methods calculates the new values and checks if any values have
    changed from the past values (from config file).Any updates are propogated
    to both config and kernel. 
    """
    with open(CONFIG_ROOT + CONFIG_ENV_ATTRS_FILE) as f:
        attrs = json.load(f)
    old_day = attrs["env"].get("day")
    old_time = attrs["env"].get("time")
    current_day = update_day_env()
    current_time = update_time_env()
    print(datetime.datetime.now())
    print("Old environment attributes")
    print(f"DAY: {old_day}")
    print(f"TIME: {old_time}")
    print("Current environment attributes")
    print(f"DAY: {current_day}")
    print(f"TIME: {current_time}")
    if not force and current_day == old_day and current_time == old_time:
        print("Environment attributes unchanged.")
        return
    with open(CONFIG_ROOT + CONFIG_ENV_ATTRS_FILE, 'w') as f:
        attrs["env"]["day"] = current_day
        attrs["env"]["time"] = current_time
        json.dump(attrs, f)
    print("Updating environment attributes...")
    load_env_attr()

@click.command()
@click.option('-f', '--force', is_flag=True, default=False, help="Enable this flag for manually updating the environment attributes" )
def env_update(force):
    """
    ABAC Environment attribute service.
    Runs as a system service in the background.
    This method is automatically invoked by systemd every hour.
    It can also be invoked manually by the Root
    """
    check_root()
    if force:
        update_env(force=True)
        return
    # Initial forced update of environment variables
    update_env(force=True)
    print("Scheduling the environment attribute updater to run every hour...")
    sched = BlockingScheduler()
    # We want the update to happen every clock hour. Not at an interval of an hour.
    sched.add_job(update_env,'cron',hour="*")
    sched.start()
