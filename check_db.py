import sqlite3
import os

db_path = "epa.db"
if not os.path.exists(db_path):
    print(f"Database {db_path} does not exist!")
else:
    print(f"Database {db_path} exists. Size: {os.path.getsize(db_path)} bytes")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]
    print(f"Alert count: {alert_count}")
    
    cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5")
    alerts = cursor.fetchall()
    for alert in alerts:
        print(alert)
        
    cursor.execute("SELECT MIN(entropy), MAX(entropy), AVG(entropy) FROM entropy")
    min_e, max_e, avg_e = cursor.fetchone()
    print(f"Entropy Stats: Min={min_e:.4f}, Max={max_e:.4f}, Avg={avg_e:.4f}")
    
    cursor.execute("SELECT file, entropy FROM entropy ORDER BY entropy DESC LIMIT 10")
    top_entropy = cursor.fetchall()
    print("Top 10 Entropy Records:")
    for row in top_entropy:
        print(row)
    
    conn.close()
