# EPA Quick Usage Guide

## 🚀 Getting Started

### 1. First Time Setup
```bash
# Run automated setup
bash setup.sh
```

### 2. Running EPA System (Recommended)

The easiest way to start the system is using the provided **Makefile**:

```bash
# Start both Monitor and Dashboard simultaneously
make run
```

---

### 3. Manual Startup (Alternative)

**Terminal 1: Start EPA Monitoring**
```bash
source venv/bin/activate.fish
python main.py
```

**Terminal 2: Start Dashboard**
```bash
source venv/bin/activate.fish
cd dashboard
streamlit run app.py
```

Open browser to: http://localhost:8501

---

## 🧪 Testing & Validation

### Run Unit Tests
```bash
source venv/bin/activate
bash run_tests.sh
```

This will:
- Run all unit tests
- Generate coverage report
- Create HTML coverage report in `htmlcov/`

### Run Performance Benchmarks
```bash
source venv/bin/activate
python benchmark.py
```

Generates: `benchmark_results.json`

### Run Full Validation
```bash
source venv/bin/activate
python validate.py
```

Generates:
- `validation_results.json` - Raw data
- `VALIDATION_REPORT.md` - Formatted report

---

## 🎮 Running Simulators

> ⚠️ **Always run each attack in its own isolated folder.** Generate fresh test data before each run so attacks do not interfere with each other.

### Step 0: Generate Fresh Test Data

Each attack needs a clean directory with test files to encrypt. Run this before any simulation:

```bash
source venv/bin/activate

# Generate test data for a specific attack folder
python3 simulator/generate_test_data.py <folder-name>

# To regenerate (wipe and recreate):
python3 simulator/generate_test_data.py <folder-name> --clean
```

---

### 🚀 Attack 1 — WannaCry-Style (Fast & Furious)

**Behaviour:** Encrypts ALL common file types in-place at 500 files/sec. Drops `README_DECRYPT.txt`.

```bash
source venv/bin/activate

# Step 1: Create isolated test data
python3 simulator/generate_test_data.py test-wannacry

# Step 2: Run the attack
echo "yes" | python3 simulator/malicious/wannacry_sim.py test-wannacry --speed 500 --algorithm aes256
```

**What you'll see:**
- Every `.txt`, `.doc`, `.docx`, `.pdf`, `.jpg`, `.png`, `.xlsx`, `.zip`, `.sql`, `.bak` encrypted in-place
- `[WANNACRY] ✓ Encrypted: <file>` for each file
- `README_DECRYPT.txt` ransom note created in the folder
- Summary: files encrypted, KB processed, time elapsed

**Options:**
| Flag | Default | Description |
|---|---|---|
| `--speed N` | `500` | Files per second |
| `--algorithm` | `aes256` | `fernet`, `aes256`, or `chacha20` |

---

### 🎯 Attack 2 — LockBit-Style (Targeted & Selective)

**Behaviour:** Targets only business-critical files at 100 files/sec. Renames to `.lockbit`, deletes originals. Drops `Restore-My-Files.txt`.

```bash
source venv/bin/activate

# Step 1: Create isolated test data
python3 simulator/generate_test_data.py test-lockbit

# Step 2: Run the attack
echo "yes" | python3 simulator/malicious/lockbit_sim.py test-lockbit --speed 100 --algorithm fernet
```

**What you'll see:**
- Only `.xlsx`, `.xls`, `.sql`, `.bak`, `.docx`, `.doc`, `.pptx`, `.ppt` targeted
- `[LOCKBIT] ✓ report.doc → report.doc.lockbit` (originals deleted)
- `Restore-My-Files.txt` ransom note created
- Breakdown by extension before encryption starts

**Options:**
| Flag | Default | Description |
|---|---|---|
| `--speed N` | `100` | Files per second |
| `--algorithm` | `fernet` | `fernet`, `aes256`, or `chacha20` |

---

### 🐢 Attack 3 — Ryuk-Style (Slow & Stealthy)

**Behaviour:** Prioritises high-value files (`.sql`, `.bak`, `.xlsx`, `.docx`) first, then secondary targets. Renames to `.ryk`, deletes originals. Drops `RyukReadMe.txt`.

```bash
source venv/bin/activate

# Step 1: Create isolated test data
python3 simulator/generate_test_data.py test-ryuk

# Step 2a: Real stealth simulation (default — 5 files/minute, very slow)
echo "yes" | python3 simulator/malicious/ryuk_sim.py test-ryuk --speed 5 --algorithm aes256

# Step 2b: Quick testing (sped up)
echo "yes" | python3 simulator/malicious/ryuk_sim.py test-ryuk --speed 300 --algorithm aes256
```

**What you'll see:**
- `⭐` marking priority targets (`.sql`, `.bak`, `.xlsx`) in the breakdown
- Progress counter: `[RYUK] Progress: 1/45`
- `[RYUK] ✓ Encrypted: backup.sql → backup.sql.ryk` (originals deleted)
- `RyukReadMe.txt` ransom note created
- Estimated duration shown before starting

**Options:**
| Flag | Default | Description |
|---|---|---|
| `--speed N` | `5` | Files per **minute** (not per second!) |
| `--algorithm` | `aes256` | `fernet`, `aes256`, or `chacha20` |

---

### ✅ Benign Activities (Should NOT Trigger Alerts)

These simulate legitimate software that produces high-entropy output, used to validate zero false positives.

```bash
source venv/bin/activate

# Backup compression (50 files/sec, creates .zip archive)
python3 simulator/benign/backup_sim.py test-folder/

# Database writes (SQLite with encrypted blobs)
python3 simulator/benign/database_sim.py test-folder/

# Video encoding (creates fake .mp4 files, 1 video/minute)
python3 simulator/benign/video_sim.py test-folder/
```

---

### 🔑 Quick Reference

| Attack | Script | Speed | Extension | Ransom Note |
|---|---|---|---|---|
| WannaCry | `simulator/malicious/wannacry_sim.py` | 500 files/sec | in-place | `README_DECRYPT.txt` |
| LockBit | `simulator/malicious/lockbit_sim.py` | 100 files/sec | `.lockbit` | `Restore-My-Files.txt` |
| Ryuk | `simulator/malicious/ryuk_sim.py` | 5 files/min | `.ryk` | `RyukReadMe.txt` |

---

## 📊 For Project Report

### Generate All Metrics
```bash
# 1. Run tests with coverage
bash run_tests.sh

# 2. Run benchmarks
python benchmark.py

# 3. Run validation
python validate.py
```

### Files for Report
- `benchmark_results.json` - Performance metrics
- `validation_results.json` - Detection accuracy
- `VALIDATION_REPORT.md` - Formatted validation report
- `htmlcov/index.html` - Code coverage report

---

## 🔧 Configuration

Edit `config.yaml`:
```yaml
watch_path: test-folder
entropy_sample_size: 4096
zscore_threshold: 3.0
rolling_window: 10
cusum_drift: 0.1
cusum_threshold: 1.5
```

---

## 📝 Common Tasks

### Reset Test Data
```bash
python simulator/generate_test_data.py test-folder/ --clean
```

### Check Database
```bash
python check_db.py
```

### View Logs
EPA prints to console - redirect to file:
```bash
python main.py > epa.log 2>&1
```

---

## ✅ Pre-Submission Checklist

- [ ] Run `bash run_tests.sh` - All tests pass
- [ ] Run `python benchmark.py` - Get performance metrics
- [ ] Run `python validate.py` - Get accuracy metrics
- [ ] Update README.md with team information
- [ ] Take screenshots of dashboard
- [ ] Record demo video (optional)
- [ ] Review all generated reports

---

## 🆘 Troubleshooting

**EPA not detecting:**
- Check config.yaml watch_path matches test folder
- Verify EPA is running: `ps aux | grep main.py`
- Check database: `python check_db.py`

**Tests failing:**
- Activate virtual environment first
- Install test dependencies: `pip install coverage pytest`
- Check Python version: `python3 --version` (need 3.8+)

**Dashboard not loading:**
- Check port 8501 is not in use
- Try different port: `streamlit run app.py --server.port 8502`

---

For detailed documentation, see:
- `README.md` - Full project documentation
- `MVP_GUIDE.md` - Detailed usage guide
- `simulator/README.md` - Simulator documentation
