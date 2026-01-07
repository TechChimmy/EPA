import sys
import os
import sqlite3
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------
# Ensure project root is available for imports
# -------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DB_PATH = os.path.join(ROOT_DIR, "epa.db")

# -------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="EPA – Ransomware Entropy Pattern Analyzer",
    layout="wide"
)

st.title("🛡️ EPA – Ransomware Entropy Pattern Analyzer")
st.caption("📁 Monitoring folder: test-folder")

# -------------------------------------------------
# Auto refresh every 2 seconds (STABLE)
# -------------------------------------------------
st_autorefresh(interval=2000, key="epa_refresh")

# -------------------------------------------------
# Database Connection
# -------------------------------------------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# -------------------------------------------------
# ENTROPY TRENDS SECTION
# -------------------------------------------------
st.subheader("📈 File Entropy Trends")

entropy_df = pd.read_sql(
    "SELECT file, entropy, timestamp FROM entropy ORDER BY timestamp ASC",
    conn
)

if not entropy_df.empty:
    selected_file = st.selectbox(
        "Select file to visualize entropy",
        entropy_df["file"].unique()
    )

    plot_df = entropy_df[entropy_df["file"] == selected_file]
    plot_df = plot_df.set_index("timestamp")

    st.line_chart(plot_df["entropy"])
else:
    st.info("Waiting for file activity...")

# -------------------------------------------------
# ALERTS SECTION
# -------------------------------------------------
st.subheader("🚨 Ransomware Alerts")

alerts_df = pd.read_sql(
    "SELECT file, entropy, message, timestamp FROM alerts ORDER BY timestamp DESC",
    conn
)

if not alerts_df.empty:
    st.dataframe(alerts_df, use_container_width=True)
else:
    st.success("No ransomware activity detected.")

conn.close()
