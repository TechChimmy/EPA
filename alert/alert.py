from shared.db import get_conn

def raise_alert(file, entropy, message):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO alerts (file, entropy, message) VALUES (?, ?, ?)",
        (file, entropy, message)
    )

    conn.commit()
    conn.close()
