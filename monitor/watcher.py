from watchdog.events import FileSystemEventHandler
from monitor.sampler import sample_file
from monitor.process import get_process_info
from entropy.entropy import shannon_entropy
from entropy.rolling import RollingEntropy
from detection.zscore import is_anomaly
from detection.cusum import CUSUM
from alert.alert import raise_alert
from shared.state import entropy_history
from shared.db import get_conn
import os
import time


class Watcher(FileSystemEventHandler):
    def __init__(self, sample_size=4096, threshold=3.0, cusum_drift=0.1, cusum_threshold=1.5):
        self.sample_size = sample_size
        self.threshold = threshold
        self.cusum_drift = cusum_drift
        self.cusum_threshold = cusum_threshold
        self.store = {}  # Rolling entropy windows per file
        self.cusum_store = {}  # CUSUM detectors per file
        self.last_processed = {}  # timestamp of last processing per file

    def on_modified(self, event):
        self._process_event(event)

    def on_created(self, event):
        self._process_event(event)

    def _process_event(self, event):
        if event.is_directory or event.src_path.endswith(('.db', '.db-journal', '.log')):
            return

        # Debounce: Skip if we processed this exact file in the last 1.0 seconds
        # This prevents duplicate alerts from both on_created and on_modified
        current_time = time.time()
        if event.src_path in self.last_processed:
            if current_time - self.last_processed[event.src_path] < 1.0:
                return

        self.last_processed[event.src_path] = current_time
        print(f"[DEBUG] Processing ({event.event_type}): {event.src_path}")

        # Get process information for the modifying process
        # Note: watchdog doesn't provide PID, so we get current process info
        # In a real implementation, we'd use inotify directly to get the actual PID
        process_info = self._get_file_modifier_process(event.src_path)

        data = sample_file(event.src_path, self.sample_size)
        if not data:
            print(f"[DEBUG] Failed to sample file: {event.src_path}")
            return

        entropy = shannon_entropy(data)
        print(f"[DEBUG] Entropy for {event.src_path}: {entropy:.4f}")
        
        # Log to DB
        log_entropy(event.src_path, entropy)

        entropy_history.setdefault(event.src_path, []).append(entropy)

        # Initialize rolling entropy window if needed
        if event.src_path not in self.store:
            self.store[event.src_path] = RollingEntropy()

        rolling = self.store[event.src_path]
        rolling.add(entropy)

        # Initialize CUSUM detector if needed
        if event.src_path not in self.cusum_store:
            self.cusum_store[event.src_path] = CUSUM(
                drift=self.cusum_drift,
                threshold=self.cusum_threshold
            )

        # DETECTION LAYER 1: Immediate high-entropy detection
        # For ransomware, we often only see ONE modification.
        # If entropy is high (> 5.5), alert immediately.
        # (Base64 encoded ciphertext has entropy ~6.0, raw ciphertext ~8.0)
        if entropy > 5.5:
            raise_alert(
                event.src_path,
                entropy,
                f"Critical: High entropy detected on first modification ({entropy:.2f})",
                process_info
            )
            return

        # DETECTION LAYER 2: CUSUM for slow attacks
        # Update CUSUM with normalized entropy deviation
        cusum = self.cusum_store[event.src_path]
        if rolling.count >= 2:
            mean, std = rolling.stats()
            if std and std > 0:
                # Normalize entropy deviation
                deviation = (entropy - mean) / std
                if cusum.update(deviation):
                    raise_alert(
                        event.src_path,
                        entropy,
                        f"CUSUM threshold exceeded - slow attack detected (cumulative deviation)",
                        process_info
                    )
                    return

        # DETECTION LAYER 3: Z-score statistical detection
        # Wait for baseline before statistical detection
        if rolling.count < 5:
            return

        mean, std = rolling.stats()

        if std and is_anomaly(entropy, mean, std, self.threshold):
            raise_alert(
                event.src_path,
                entropy,
                f"Abnormal entropy spike detected (z>{self.threshold})",
                process_info
            )

    def _get_file_modifier_process(self, filepath):
        """
        Attempt to identify the process modifying the file
        
        Note: This is a simplified implementation. On Linux, we could use:
        - /proc/*/fd/* to find which process has the file open
        - inotify with process tracking
        - eBPF/ftrace for kernel-level monitoring
        
        For MVP, we'll try to find the process with the file open
        """
        try:
            import psutil
            
            # Try to find process with this file open
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    open_files = proc.info.get('open_files')
                    if open_files:
                        for f in open_files:
                            if f.path == filepath:
                                return get_process_info(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        
        # Fallback: return None (no process attribution)
        return None


def log_entropy(event_src_path, entropy):
    """Log entropy measurement to database"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
            (event_src_path, entropy)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to log entropy: {e}")