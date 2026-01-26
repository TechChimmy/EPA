import psutil
import os

# Common ransomware process indicators
SUSPICIOUS_PROCESS_NAMES = [
    'wannacry', 'ryuk', 'lockbit', 'revil', 'sodinokibi', 
    'conti', 'maze', 'egregor', 'darkside', 'blackmatter',
    'encrypt', 'ransom', 'crypt', 'locker'
]

def get_process_info(pid=None):
    """
    Get process information for a given PID or current process
    
    Args:
        pid: Process ID to query (None for current process)
        
    Returns:
        dict: Process information including pid, name, cmdline, parent
    """
    try:
        if pid is None:
            p = psutil.Process()
        else:
            p = psutil.Process(pid)
            
        # Get parent process info
        parent_info = "N/A"
        try:
            parent = p.parent()
            if parent:
                parent_info = f"{parent.name()} (PID: {parent.pid})"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return {
            "pid": p.pid,
            "name": p.name(),
            "cmdline": " ".join(p.cmdline()) if p.cmdline() else "N/A",
            "parent": parent_info,
            "suspicious": is_suspicious_process(p.name(), p.cmdline())
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
        return {
            "pid": pid or os.getpid(),
            "name": "Unknown",
            "cmdline": "N/A",
            "parent": "N/A",
            "suspicious": False
        }

def get_process_tree(pid):
    """
    Get the process tree (ancestors) for a given PID
    
    Args:
        pid: Process ID to query
        
    Returns:
        list: List of ancestor processes
    """
    tree = []
    try:
        p = psutil.Process(pid)
        while p:
            try:
                tree.append({
                    "pid": p.pid,
                    "name": p.name(),
                    "cmdline": " ".join(p.cmdline()) if p.cmdline() else "N/A"
                })
                p = p.parent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    except Exception:
        pass
    
    return tree

def is_suspicious_process(name, cmdline=None):
    """
    Check if a process name or command line contains suspicious indicators
    
    Args:
        name: Process name
        cmdline: Process command line (optional)
        
    Returns:
        bool: True if process appears suspicious
    """
    if not name:
        return False
    
    name_lower = name.lower()
    
    # Check process name
    for indicator in SUSPICIOUS_PROCESS_NAMES:
        if indicator in name_lower:
            return True
    
    # Check command line if available
    if cmdline:
        cmdline_lower = cmdline.lower() if isinstance(cmdline, str) else " ".join(cmdline).lower()
        for indicator in SUSPICIOUS_PROCESS_NAMES:
            if indicator in cmdline_lower:
                return True
    
    return False
