import psutil

def get_process_info():
    try:
        p = psutil.Process()
        return {
            "pid": p.pid,
            "name": p.name()
        }
    except Exception:
        return {}
