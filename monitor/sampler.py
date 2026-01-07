def sample_file(path, size=4096):
    try:
        with open(path, "rb") as f:
            return f.read(size)
    except Exception:
        return b""
