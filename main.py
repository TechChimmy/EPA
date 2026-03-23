import time
import yaml
from watchdog.observers import Observer
from monitor.watcher import Watcher
from shared.db import init_db

# Initialize database
print("🛡️ EPA - Entropy-based Process Anomaly Detection")
print("=" * 50)
init_db()

with open("config.yaml") as f:
    config = yaml.safe_load(f)

path = config["watch_path"]

event_handler = Watcher(
    sample_size=config.get("entropy_sample_size", 4096),
    threshold=config.get("zscore_threshold", 3.0),
    cusum_drift=config.get("cusum_drift", 0.1),
    cusum_threshold=config.get("cusum_threshold", 1.5)
)

event_handler.initial_scan(path)

observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

# Start background process tracker for reliable process attribution
event_handler.start_process_tracker(path)

print(f"🔍 Monitoring: {path}")
print(f"📊 Detection Methods:")
print(f"   - High Entropy (>5.5): Immediate alert")
print(f"   - CUSUM (drift={config.get('cusum_drift', 0.1)}, threshold={config.get('cusum_threshold', 1.5)}): Slow attack detection")
print(f"   - Z-score (threshold={config.get('zscore_threshold', 3.0)}): Statistical anomaly detection")
print("=" * 50)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    event_handler.stop_process_tracker()
    observer.stop()

observer.join()
