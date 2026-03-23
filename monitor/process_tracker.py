"""
Background process tracker for reliable process attribution.

Solves the race condition where file handles are closed before
psutil can scan for them by continuously polling and caching
which processes have files open in the monitored directory.
"""

import threading
import time
import os
import psutil
from monitor.process import get_process_info


class ProcessTracker:
    """
    Tracks processes accessing files in a monitored directory.

    Uses two strategies:
    1. Background polling: Continuously scans process open_files and caches results
    2. Command-line matching: Finds processes whose argv references the target directory
    """

    def __init__(self, watch_path, poll_interval=0.2):
        self.watch_path = os.path.abspath(watch_path)
        self.poll_interval = poll_interval
        # filepath -> {pid, name, timestamp}
        self._file_cache = {}
        # directory -> {pid, name, timestamp}  (most recent process per directory)
        self._dir_cache = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        """Start the background polling thread."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background polling thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _poll_loop(self):
        """Continuously scan processes for open file handles."""
        while self._running:
            try:
                self._scan_processes()
            except Exception:
                pass
            time.sleep(self.poll_interval)

    def _scan_processes(self):
        """Scan all processes and cache those with files open in the watch path."""
        now = time.time()
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                open_files = proc.info.get('open_files')
                if not open_files:
                    continue
                for f in open_files:
                    abs_path = os.path.abspath(f.path)
                    if abs_path.startswith(self.watch_path):
                        entry = {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'timestamp': now
                        }
                        with self._lock:
                            self._file_cache[abs_path] = entry
                            self._dir_cache[os.path.dirname(abs_path)] = entry
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def lookup(self, filepath, max_age=5.0):
        """
        Look up the process that recently accessed a file.

        Strategy order:
        1. Exact file match from cache
        2. Directory match from cache (same dir, most recent)
        3. Command-line match (process argv references the file's directory)

        Args:
            filepath: Absolute path to the file
            max_age: Maximum age in seconds for cached entries

        Returns:
            dict with process info, or None
        """
        now = time.time()
        abs_path = os.path.abspath(filepath)
        file_dir = os.path.dirname(abs_path)

        with self._lock:
            # Strategy 1: Exact file match
            if abs_path in self._file_cache:
                entry = self._file_cache[abs_path]
                if now - entry['timestamp'] < max_age:
                    return get_process_info(entry['pid'])

            # Strategy 2: Directory match
            if file_dir in self._dir_cache:
                entry = self._dir_cache[file_dir]
                if now - entry['timestamp'] < max_age:
                    return get_process_info(entry['pid'])

        # Strategy 3: Command-line matching (outside lock, slower)
        return self._match_by_cmdline(file_dir)

    def _match_by_cmdline(self, target_dir):
        """
        Find a process whose command line references the target directory.

        This catches long-running processes (like simulators) that have
        already closed individual file handles but are still running with
        the target directory as an argument.
        """
        # Normalize for comparison
        target_dir_abs = os.path.abspath(target_dir)
        # Also check the relative form (e.g., "test-folder")
        target_dir_rel = os.path.basename(target_dir_abs)

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if not cmdline:
                    continue

                # Skip system processes and our own EPA process
                name = proc.info.get('name', '')
                if name in ('python3', 'python', 'python3.10', 'python3.11', 'python3.12'):
                    cmdline_str = ' '.join(cmdline)
                    # Check if any cmdline arg matches the target directory
                    for arg in cmdline:
                        arg_abs = os.path.abspath(arg) if not arg.startswith('-') else ''
                        if arg_abs == target_dir_abs or arg == target_dir_rel:
                            # Found a Python process targeting this directory
                            # Skip if it's the EPA monitor itself (main.py)
                            if 'main.py' in cmdline_str or 'app.py' in cmdline_str:
                                continue
                            return get_process_info(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return None
