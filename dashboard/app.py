import sys
import os
import sqlite3
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
import yaml

# -------------------------------------------------
# Ensure project root is available for imports
# -------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DB_PATH = os.path.join(ROOT_DIR, "epa.db")
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")

# -------------------------------------------------
# Load Config
# -------------------------------------------------
def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {
            "zscore_threshold": 3.0,
            "rolling_window": 10,
            "cusum_drift": 0.1,
            "cusum_threshold": 1.5
        }

config = load_config()

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
# SIMULATOR CONTROL (SIDEBAR)
# -------------------------------------------------
with st.sidebar:
    st.header("🎮 Simulator Control")
    st.caption("Trigger simulations in `test-folder`")
    
    # Target directory (hardcoded for now, matches config)
    TARGET_DIR = "test-folder"
    
    import subprocess
    
    def run_simulation(script_path, name):
        """Run a simulation script in a subprocess"""
        try:
            full_path = os.path.join(ROOT_DIR, script_path)
            # Use same python executable
            subprocess.Popen([sys.executable, full_path, TARGET_DIR])
            st.toast(f"🚀 Started {name}!")
        except Exception as e:
            st.error(f"Failed to start {name}: {e}")

    st.subheader("⚠️ Malicious Attacks")
    if st.button("🦠 WannaCry (Fast Encrypt)", type="primary"):
        run_simulation("simulator/malicious/wannacry_sim.py", "WannaCry")
        
    if st.button("👹 Ryuk (Slow Encrypt)", type="primary"):
        run_simulation("simulator/malicious/ryuk_sim.py", "Ryuk")
        
    if st.button("🔒 LockBit (Targeted)", type="primary"):
        run_simulation("simulator/malicious/lockbit_sim.py", "LockBit")
        
    st.divider()
    
    st.subheader("✅ Benign Activity")
    if st.button("📦 Backup (Compression)"):
        run_simulation("simulator/benign/backup_sim.py", "Backup")
        
    if st.button("🗄️ Database (Activity)"):
        run_simulation("simulator/benign/database_sim.py", "Database")
    
    if st.button("🎥 Video (Processing)"):
        run_simulation("simulator/benign/video_sim.py", "Video")

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

# -------------------------------------------------
# PROCESS ACTIVITY BREAKDOWN
# -------------------------------------------------
st.divider()
st.subheader("🖥️ Process Activity Breakdown")

try:
    process_df = pd.read_sql(
        """SELECT process_name, process_id, COUNT(*) as alert_count, MAX(timestamp) as last_seen
           FROM alerts
           WHERE process_name IS NOT NULL
           GROUP BY process_name, process_id
           ORDER BY alert_count DESC""",
        conn
    )
    
    if not process_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart for alerts per process
            fig = px.bar(
                process_df, 
                x='process_name', 
                y='alert_count',
                color='process_name',
                labels={'process_name': 'Process', 'alert_count': 'Alert Count'},
                title="Alerts per Process"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.metric("Most Active Process", process_df.iloc[0]['process_name'], f"{process_df.iloc[0]['alert_count']} alerts")
            st.dataframe(process_df[['process_name', 'alert_count', 'last_seen']], hide_index=True)
    else:
        st.info("No process activity data yet.")

except Exception as e:
    st.error(f"Error loading process activity: {e}")

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
        
        # --- CUSUM and Z-score charts ---
        st.subheader("📉 CUSUM and Z-Score Trends")
        
        # 1. CUSUM Logic
        drift = config.get("cusum_drift", 0.1)
        threshold = config.get("cusum_threshold", 1.5)
        
        cusum_scores = []
        current_sum = 0
        for val in plot_df["entropy"]:
            current_sum = max(0, current_sum + val - drift)
            cusum_scores.append(current_sum)
        
        plot_df["cusum"] = cusum_scores
        
        # 2. Z-Score Logic
        window = config.get("rolling_window", 10)
        z_threshold = config.get("zscore_threshold", 3.0)
        
        plot_df["rolling_mean"] = plot_df["entropy"].rolling(window=window).mean()
        plot_df["rolling_std"] = plot_df["entropy"].rolling(window=window).std()
        plot_df["zscore"] = (plot_df["entropy"] - plot_df["rolling_mean"]) / plot_df["rolling_std"]
        plot_df["zscore"] = plot_df["zscore"].abs().fillna(0)
        
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            # CUSUM Plot with threshold line
            fig_cusum = go.Figure()
            fig_cusum.add_trace(go.Scatter(x=plot_df.index, y=plot_df["cusum"], name="CUSUM Score", line=dict(color='orange')))
            fig_cusum.add_hline(y=threshold, line_dash="dash", line_color="red", annotation_text="Threshold")
            fig_cusum.update_layout(title="CUSUM Trend", height=300, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_cusum, use_container_width=True)
            
        with c_col2:
            # Z-Score Plot with threshold line
            fig_z = go.Figure()
            fig_z.add_trace(go.Scatter(x=plot_df.index, y=plot_df["zscore"], name="Z-Score", line=dict(color='cyan')))
            fig_z.add_hline(y=z_threshold, line_dash="dash", line_color="red", annotation_text="Z=3.0")
            fig_z.update_layout(title="Z-Score Trend", height=300, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_z, use_container_width=True)
        
        # Show statistics for selected file
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Min Entropy", f"{plot_df['entropy'].min():.2f}")
        with col2:
            st.metric("Max Entropy", f"{plot_df['entropy'].max():.2f}")
        with col3:
            st.metric("Max CUSUM", f"{plot_df['cusum'].max():.2f}")
    else:
        st.info("⏳ Waiting for file activity...")

except Exception as e:
    st.error(f"Error loading entropy trends: {e}")

# -------------------------------------------------
# ALERT FREQUENCY TIMELINE
# -------------------------------------------------
st.divider()
st.subheader("📅 Alert Frequency History")

try:
    timeline_df = pd.read_sql(
        "SELECT message, timestamp FROM alerts ORDER BY timestamp ASC",
        conn
    )
    
    if not timeline_df.empty:
        timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
        
        # Histogram showing alerts clustered by time
        fig_hist = px.histogram(
            timeline_df, 
            x="timestamp", 
            color="message",
            marginal="rug",
            nbins=30,
            title="Alerts Over Time",
            labels={'timestamp': 'Time', 'count': 'Number of Alerts'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No alert history yet.")

except Exception as e:
    st.error(f"Error loading timeline: {e}")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()
st.caption("EPA - Entropy-based Process Anomaly Detection | Auto-refreshing every 2 seconds")

conn.close()
