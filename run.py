from app import app
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hypercorn.asyncio
import hypercorn.config
import asyncio
import os
import sys

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, restart):
        self.restart = restart

    def on_any_event(self, event):
        if event.event_type in ['modified', 'created', 'deleted'] and event.src_path.endswith('.py'):
            self.restart()

def restart_server():
    print("Changes detected. Restarting server...")
    os.execv(sys.executable, ['python'] + sys.argv)

def start_watchdog():
    event_handler = ChangeHandler(restart_server)
    observer = Observer()
    observer.schedule(event_handler, path='app', recursive=True)
    observer.start()

if __name__ == '__main__':
    start_watchdog()
    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:5001"]
    asyncio.run(hypercorn.asyncio.serve(app, config))
