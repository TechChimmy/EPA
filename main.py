import time
import yaml
from watchdog.observers import Observer
from monitor.watcher import Watcher

with open("config.yaml") as f:
    config = yaml.safe_load(f)

path = config["watch_path"]

event_handler = Watcher(
    sample_size=config["entropy_sample_size"],
    threshold=config["zscore_threshold"]
)

observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

print("🛡️ EPA-Lite running... Monitoring:", path)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
