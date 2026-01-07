from watchdog.events import FileSystemEventHandler
from monitor.sampler import sample_file
from entropy.entropy import shannon_entropy
from entropy.rolling import RollingEntropy
from detection.zscore import is_anomaly
from alert.alert import raise_alert
from shared.state import entropy_history
from shared.db import get_conn


class Watcher(FileSystemEventHandler):
    def __init__(self, sample_size=4096, threshold=3.0):
        self.sample_size = sample_size
        self.threshold = threshold
        self.store = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        data = sample_file(event.src_path, self.sample_size)
        if not data:
            return

        entropy = shannon_entropy(data)

        entropy_history.setdefault(event.src_path, []).append(entropy)

        if event.src_path not in self.store:
            self.store[event.src_path] = RollingEntropy()

        rolling = self.store[event.src_path]
        rolling.add(entropy)

        # Wait for baseline
        if rolling.count < 5:
            return

        mean, std = rolling.stats()

        if std and is_anomaly(entropy, mean, std, self.threshold):
            raise_alert(
                event.src_path,
                entropy,
                f"Abnormal entropy spike detected (z>{self.threshold})"
            )


def log_entropy(event_src_path, entropy):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
        (event_src_path, entropy)
    )
    conn.commit()
    conn.close()