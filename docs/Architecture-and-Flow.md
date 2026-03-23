# EPA - How It Works

## The Problem

Ransomware encrypts your files. Encrypted data looks like random noise — it has **high entropy** (randomness). Normal files (documents, photos) have **low entropy** (structured data). EPA exploits this difference.

## The Flow (Step by Step)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────────┐
│  File System │────▶│  File Watcher │────▶│ Entropy Calculator│────▶│ Detection │
│  (test-folder)│     │  (watchdog)  │     │  (Shannon formula)│     │  Engine   │
└─────────────┘     └──────────────┘     └─────────────────┘     └─────┬─────┘
                                                                       │
                                                          ┌────────────┼────────────┐
                                                          ▼            ▼            ▼
                                                      Layer 1      Layer 2      Layer 3
                                                    High Entropy    CUSUM       Z-Score
                                                     (> 5.5)      (gradual)  (statistical)
                                                          │            │            │
                                                          └────────────┼────────────┘
                                                                       ▼
                                                    ┌──────────────────────────────┐
                                                    │  Alert + Process Attribution │
                                                    │  (Who encrypted this file?)  │
                                                    └──────────────┬───────────────┘
                                                                   ▼
                                                          ┌─────────────────┐
                                                          │  SQLite Database │
                                                          │  + Dashboard     │
                                                          └─────────────────┘
```

## Each Component in Plain English

### 1. File Watcher (`monitor/watcher.py`)

- Uses the `watchdog` library to listen for any file being created or modified in the monitored directory.
- Think of it as a CCTV camera watching a folder — the moment any file changes, it triggers an event.

### 2. Entropy Calculator (`entropy/entropy.py`)

- Reads the first 4096 bytes of the changed file.
- Applies **Shannon entropy** formula — a mathematical measure of randomness.
- Normal `.txt` file → entropy ~3-4 bits/byte
- Encrypted file → entropy ~6-8 bits/byte

### 3. Three-Layer Detection Engine

This is the core innovation:

| Layer | Method | What It Catches | How |
|-------|--------|----------------|-----|
| **Layer 1** | High Entropy (>5.5) | Fast attacks (WannaCry) | If a file's entropy is immediately very high, alert instantly. No history needed. |
| **Layer 2** | CUSUM | Slow/stealthy attacks (Ryuk) | Accumulates small deviations over time. Even if each file change looks small, the cumulative drift triggers an alert. |
| **Layer 3** | Z-Score | Statistical outliers | Compares current entropy against the rolling average. If it's more than 3 standard deviations away, it's anomalous. |

### 4. Process Attribution (`monitor/process_tracker.py`)

- After detecting suspicious activity, EPA identifies **which process** encrypted the file.
- Runs a background thread that continuously tracks which processes have files open in the monitored directory.
- Answers the question: *"Not just that an attack happened, but who did it."*

### 5. Dashboard (`dashboard/app.py`)

- Real-time Streamlit web interface, refreshes every 2 seconds.
- Shows: alerts, entropy graphs, attack timeline, process info.
- Has buttons to trigger test simulations (WannaCry, Ryuk, LockBit).

## How We Test It

We built **three ransomware simulators** that mimic real attack patterns:

| Simulator | Real-World Equivalent | Behavior |
|-----------|----------------------|----------|
| **WannaCry** | Fast & destructive | Encrypts everything rapidly (500 files/sec) |
| **Ryuk** | Slow & targeted | Encrypts slowly (5 files/min), targets databases |
| **LockBit** | Selective | Targets only business-critical files (.xlsx, .sql, .doc) |

We also have **benign simulators** (backup, database, video) to prove EPA doesn't trigger false alarms on legitimate high-entropy operations.

## One-Line Summary

> EPA watches files in real-time, measures their randomness using Shannon entropy, and uses three statistical detection methods to catch ransomware — whether it's fast, slow, or stealthy — while identifying the exact malicious process responsible.
