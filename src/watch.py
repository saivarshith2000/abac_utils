# ABAC Shared Directory watch
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

import time
import click
import json
from subprocess import Popen, PIPE
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .common import check_root
from .config import SHARED_DIR, CONFIG_ROOT, CONFIG_OBJ_ATTRS_FILE
from .load import load_obj_attr

watch_dir = str(Path(SHARED_DIR).resolve())

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.event_type == 'created':
            p = Popen(["chmod", "-R" , "3770", watch_dir], stdout=PIPE, stderr=PIPE)
            output, error = p.communicate()
            if p.returncode != 0: 
                print(f"Failed to chmod for {event.src_path}")
        if event.event_type == "deleted":
            # check if the deleted object has attributes, delete these attributes from config and reload
            with open(CONFIG_ROOT + CONFIG_OBJ_ATTRS_FILE) as f:
                attrs = json.load(f)
            if str(Path(event.src_path).resolve()) in attrs["objects"]:
                del attrs["objects"][event.src_path]
                print(f"Deleted attributes for file {event.src_path}")
            with open(CONFIG_ROOT + CONFIG_OBJ_ATTRS_FILE, 'w') as f:
                json.dump(attrs, f)
            load_obj_attr()

class ABACWatcher:
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, watch_dir, recursive=True)
        self.observer.start()
        try:
            print(f"Starting watching {watch_dir}")
            while True:
                time.sleep(5)
        except Exception as e:
            self.observer.stop()
            print(f"An error occured while watching {watch_dir}")
            print(e)

        self.observer.join()

@click.command()
def watch():
    """
    ABAC Shared directory watcher service. Updates permissions based on file activities.
    Runs as a system service in the background.
    """
    check_root()
    w = ABACWatcher()
    w.run()
