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
    layout="wide",
    page_icon="🛡️"
)

st.title("🛡️ EPA – Ransomware Entropy Pattern Analyzer")
st.caption("Real-time ransomware detection using entropy analysis")

# -------------------------------------------------
# Auto refresh every 2 seconds
# -------------------------------------------------
st_autorefresh(interval=2000, key="epa_refresh")

# -------------------------------------------------
# Database Connection
# -------------------------------------------------
try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
except Exception as e:
    st.error(f"❌ Failed to connect to database: {e}")
    st.stop()

# -------------------------------------------------
# SYSTEM STATUS SECTION
# -------------------------------------------------
st.subheader("📊 System Status")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get alert count
    alert_count = pd.read_sql("SELECT COUNT(*) as count FROM alerts", conn).iloc[0]['count']
    
    # Get monitored files count
    files_count = pd.read_sql("SELECT COUNT(DISTINCT file) as count FROM entropy", conn).iloc[0]['count']
    
    # Get entropy statistics
    entropy_stats = pd.read_sql(
        "SELECT MIN(entropy) as min, MAX(entropy) as max, AVG(entropy) as avg FROM entropy",
        conn
    ).iloc[0]
    
    with col1:
        st.metric("🚨 Total Alerts", alert_count, delta=None if alert_count == 0 else f"+{alert_count}")
    
    with col2:
        st.metric("📁 Files Monitored", files_count)
    
    with col3:
        if pd.notna(entropy_stats['avg']):
            st.metric("📈 Avg Entropy", f"{entropy_stats['avg']:.2f}")
        else:
            st.metric("📈 Avg Entropy", "N/A")
    
    with col4:
        if pd.notna(entropy_stats['max']):
            st.metric("⚡ Max Entropy", f"{entropy_stats['max']:.2f}")
        else:
            st.metric("⚡ Max Entropy", "N/A")

except Exception as e:
    st.error(f"Error loading system status: {e}")

st.divider()

# -------------------------------------------------
# ALERTS SECTION
# -------------------------------------------------
st.subheader("🚨 Ransomware Alerts")

try:
    alerts_df = pd.read_sql(
        """SELECT file, entropy, message, process_id, process_name, 
                  process_cmdline, timestamp 
           FROM alerts 
           ORDER BY timestamp DESC 
           LIMIT 100""",
        conn
    )
    
    if not alerts_df.empty:
        # Format display columns FIRST
        display_df = alerts_df[['timestamp', 'file', 'entropy', 'message', 'process_name', 'process_id']].copy()
        
        # Apply color coding based on message content (before renaming)
        # Using darker colors that work better in dark mode
        def get_row_color(message):
            if pd.isna(message):
                return '#1e3a5f'  # Dark blue for unknown
            if 'Critical' in str(message):
                return '#8b0000'  # Dark red for critical
            elif 'CUSUM' in str(message):
                return '#8b6914'  # Dark gold for CUSUM
            else:
                return '#1e3a5f'  # Dark blue for others
        
        # Add background color column
        display_df['_bg_color'] = display_df['message'].apply(get_row_color)
        
        # Now rename columns for display
        display_df = display_df.rename(columns={
            'timestamp': 'Time',
            'file': 'File',
            'entropy': 'Entropy',
            'message': 'Detection Method',
            'process_name': 'Process',
            'process_id': 'PID'
        })
        
        # Apply styling using the background color column
        def highlight_row(row):
            color = row['_bg_color']
            return [f'background-color: {color}'] * len(row)
        
        # Drop the helper column before displaying
        styled_df = display_df.drop(columns=['_bg_color']).style.apply(
            lambda row: [f'background-color: {display_df.loc[row.name, "_bg_color"]}'] * len(row),
            axis=1
        )
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Show detailed process info in expander
        if alerts_df['process_cmdline'].notna().any():
            with st.expander("🔍 View Detailed Process Information"):
                for idx, row in alerts_df.iterrows():
                    if pd.notna(row['process_name']):
                        st.markdown(f"**Alert #{idx + 1}** - {row['timestamp']}")
                        st.code(f"""
Process: {row['process_name']} (PID: {row['process_id']})
Command: {row['process_cmdline']}
File: {row['file']}
Entropy: {row['entropy']:.4f}
                        """)
                        st.divider()
    else:
        st.success("✅ No ransomware activity detected.")

except Exception as e:
    st.error(f"Error loading alerts: {e}")

st.divider()

# -------------------------------------------------
# ENTROPY TRENDS SECTION
# -------------------------------------------------
st.subheader("📈 File Entropy Trends")

try:
    entropy_df = pd.read_sql(
        "SELECT file, entropy, timestamp FROM entropy ORDER BY timestamp ASC",
        conn
    )
    
    if not entropy_df.empty:
        # File selector
        selected_file = st.selectbox(
            "Select file to visualize entropy",
            entropy_df["file"].unique()
        )
        
        # Filter and plot
        plot_df = entropy_df[entropy_df["file"] == selected_file].copy()
        plot_df['timestamp'] = pd.to_datetime(plot_df['timestamp'])
        plot_df = plot_df.set_index("timestamp")
        
        # Show chart
        st.line_chart(plot_df["entropy"], use_container_width=True)
        
        # Show statistics for selected file
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Min Entropy", f"{plot_df['entropy'].min():.2f}")
        with col2:
            st.metric("Max Entropy", f"{plot_df['entropy'].max():.2f}")
        with col3:
            st.metric("Std Dev", f"{plot_df['entropy'].std():.2f}")
    else:
        st.info("⏳ Waiting for file activity...")

except Exception as e:
    st.error(f"Error loading entropy trends: {e}")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()
st.caption("EPA - Entropy-based Process Anomaly Detection | Auto-refreshing every 2 seconds")

conn.close()
