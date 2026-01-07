from watchdog.observers import Observer
from monitor.watcher import Watcher
import time
import os

WATCH_DIR = "test-folder"
os.makedirs(WATCH_DIR, exist_ok=True)

observer = Observer()
observer.schedule(Watcher(), WATCH_DIR, recursive=False)
observer.start()

print(f"[EPA] Monitoring {WATCH_DIR}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
