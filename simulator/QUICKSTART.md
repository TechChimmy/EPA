# 🚀 EPA Ransomware Simulator - Quick Start Guide

## Prerequisites

### 1. Python Environment
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Required Packages
- `cryptography` - For encryption algorithms
- `watchdog` - For file monitoring (EPA agent)
- `numpy`, `scipy` - For statistical analysis
- `streamlit`, `pandas` - For dashboard

---

## 🎯 Complete Testing Workflow

### **Step 1: Prepare Test Environment**

```bash
# Create test folder
mkdir -p test-folder

# Generate test files (140 files)
python simulator/generate_test_data.py test-folder/
```

**Output:**
```
[GENERATOR] Creating test files in test-folder
[GENERATOR] Created 140 files successfully
```

---

### **Step 2: Start EPA Monitoring**

**Terminal 1 - EPA Agent:**
```bash
# Make sure config.yaml points to test-folder
# Edit config.yaml if needed:
# watch_path: /full/path/to/test-folder

python main.py
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard
streamlit run app.py
```

**Dashboard URL:** http://localhost:8501

---

### **Step 3: Run Simulations**

#### **Option A: Malicious Attacks** (Should trigger EPA alerts)

**1. WannaCry-Style (Fast Attack)**
```bash
python simulator/malicious/wannacry_sim.py test-folder/
```
- Speed: 500 files/second
- Expected: ✅ **IMMEDIATE ALERT** (Z-score detection)
- Detection time: <10 seconds

**2. Ryuk-Style (Slow Attack)**
```bash
python simulator/malicious/ryuk_sim.py test-folder/
```
- Speed: 5 files/minute
- Expected: ✅ **DELAYED ALERT** (CUSUM detection)
- Detection time: <5 minutes

**3. LockBit-Style (Targeted Attack)**
```bash
python simulator/malicious/lockbit_sim.py test-folder/
```
- Speed: 100 files/second
- Expected: ✅ **IMMEDIATE ALERT** (Z-score detection)
- Detection time: <10 seconds

---

#### **Option B: Benign Activities** (Should NOT trigger alerts)

**1. Backup Compression**
```bash
python simulator/benign/backup_sim.py test-folder/
```
- Creates ZIP archive
- Expected: ❌ **NO ALERT** (legitimate activity)

**2. Database Operations**
```bash
python simulator/benign/database_sim.py test-folder/
```
- Creates SQLite database with encrypted data
- Expected: ❌ **NO ALERT** (legitimate activity)

**3. Video Encoding**
```bash
python simulator/benign/video_sim.py test-folder/
```
- Creates MP4 video files
- Expected: ❌ **NO ALERT** (legitimate activity)

---

## 📋 Full Test Sequence

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Generate test data
python simulator/generate_test_data.py test-folder/

# 3. Start EPA (Terminal 1)
python main.py &

# 4. Start Dashboard (Terminal 2)
cd dashboard && streamlit run app.py &

# 5. Run WannaCry simulation
python simulator/malicious/wannacry_sim.py test-folder/
# → Check dashboard for alert

# 6. Reset test data
python simulator/generate_test_data.py test-folder/ --clean

# 7. Run Ryuk simulation
python simulator/malicious/ryuk_sim.py test-folder/
# → Check dashboard for alert

# 8. Reset test data
python simulator/generate_test_data.py test-folder/ --clean

# 9. Run benign backup
python simulator/benign/backup_sim.py test-folder/
# → Verify NO alert (false positive test)
```

---

## 🎛️ Customization Options

### Custom Speed
```bash
# Very fast attack
python simulator/malicious/wannacry_sim.py test-folder/ --speed 1000

# Very slow attack
python simulator/malicious/ryuk_sim.py test-folder/ --speed 1
```

### Custom Encryption
```bash
# Use AES-256
python simulator/malicious/wannacry_sim.py test-folder/ --algorithm aes256

# Use ChaCha20
python simulator/malicious/lockbit_sim.py test-folder/ --algorithm chacha20
```

### Custom Test Data
```bash
# More files
python simulator/generate_test_data.py test-folder/ --text 100 --docs 50

# Clean before generating
python simulator/generate_test_data.py test-folder/ --clean
```

---

## 📊 Expected Results

| Simulator | Alert Expected | Method | Latency |
|-----------|---------------|--------|---------|
| WannaCry | ✅ Yes | Z-score | <10s |
| Ryuk | ✅ Yes | CUSUM | <5min |
| LockBit | ✅ Yes | Z-score | <10s |
| Backup | ❌ No | N/A | N/A |
| Database | ❌ No | N/A | N/A |
| Video | ❌ No | N/A | N/A |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'"
```bash
pip install cryptography
```

### "No files found to encrypt"
```bash
# Generate test data first
python simulator/generate_test_data.py test-folder/
```

### EPA not detecting attacks
1. Check EPA is running: `ps aux | grep main.py`
2. Check config.yaml watch path matches test-folder
3. Check dashboard at http://localhost:8501
4. Verify entropy threshold in config.yaml (default: 3.0)

### Import errors
```bash
# Make sure you're in project root
cd /home/gautam/Desktop/Gautam/projects/personal/EPA

# Activate venv
source venv/bin/activate
```

---

## 📝 Quick Reference

### All Simulators

| Simulator | Command |
|-----------|---------|
| **Generate Test Data** | `python simulator/generate_test_data.py test-folder/` |
| **WannaCry** | `python simulator/malicious/wannacry_sim.py test-folder/` |
| **Ryuk** | `python simulator/malicious/ryuk_sim.py test-folder/` |
| **LockBit** | `python simulator/malicious/lockbit_sim.py test-folder/` |
| **Backup** | `python simulator/benign/backup_sim.py test-folder/` |
| **Database** | `python simulator/benign/database_sim.py test-folder/` |
| **Video** | `python simulator/benign/video_sim.py test-folder/` |

### Help Commands
```bash
# Get help for any simulator
python simulator/malicious/wannacry_sim.py --help
python simulator/benign/backup_sim.py --help
python simulator/generate_test_data.py --help
```

---

## ✅ Success Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test data generated (140 files)
- [ ] EPA agent running (`python main.py`)
- [ ] Dashboard accessible (http://localhost:8501)
- [ ] WannaCry simulation triggers alert
- [ ] Ryuk simulation triggers alert
- [ ] Backup simulation does NOT trigger alert

---

**Ready to test! 🛡️**
