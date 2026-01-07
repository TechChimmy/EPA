# Ransomware Simulation Framework - Quick Start Guide

## 🎯 Overview

This simulation framework provides realistic ransomware attack simulations and benign activity simulations to test EPA's detection capabilities.

---

## 📁 Project Structure

```
simulator/
├── core/                       # Core utilities
│   ├── encryption.py          # Encryption algorithms
│   ├── file_selector.py       # File targeting logic
│   ├── speed_controller.py    # Rate limiting
│   └── test_data_generator.py # Test file generation
│
├── malicious/                  # Malicious attack simulators
│   ├── wannacry_sim.py        # Fast attack (500 files/sec)
│   ├── ryuk_sim.py            # Slow attack (5 files/min)
│   └── lockbit_sim.py         # Targeted attack (100 files/sec)
│
├── benign/                     # Benign activity simulators
│   ├── backup_sim.py          # Backup compression
│   ├── database_sim.py        # Database operations
│   └── video_sim.py           # Video encoding
│
└── generate_test_data.py      # Test data generator script
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install cryptography
```

### Step 2: Generate Test Data

```bash
# Generate default test files (140 files total)
python simulator/generate_test_data.py test-folder/

# Custom file counts
python simulator/generate_test_data.py test-folder/ --text 100 --docs 50 --images 30
```

### Step 3: Start EPA Monitoring

```bash
# Terminal 1: Start EPA agent
python main.py

# Terminal 2: Start dashboard
cd dashboard
streamlit run app.py
```

### Step 4: Run Simulations

#### **Malicious Attacks** (Should trigger alerts)

```bash
# WannaCry-style (fast attack)
python simulator/malicious/wannacry_sim.py test-folder/

# Ryuk-style (slow attack)
python simulator/malicious/ryuk_sim.py test-folder/

# LockBit-style (targeted attack)
python simulator/malicious/lockbit_sim.py test-folder/
```

#### **Benign Activities** (Should NOT trigger alerts)

```bash
# Backup compression
python simulator/benign/backup_sim.py test-folder/

# Database operations
python simulator/benign/database_sim.py test-folder/

# Video encoding
python simulator/benign/video_sim.py test-folder/
```

---

## 📊 Simulator Details

### Malicious Simulators

#### 1. WannaCry Simulator
- **Speed**: 500 files/second (FAST)
- **Targets**: All file types (.txt, .doc, .pdf, .jpg, etc.)
- **Behavior**: Recursive, aggressive
- **Output**: Encrypted files + ransom note

```bash
python simulator/malicious/wannacry_sim.py test-folder/ --speed 500 --algorithm fernet
```

#### 2. Ryuk Simulator
- **Speed**: 5 files/minute (SLOW)
- **Targets**: High-value files first (.sql, .bak, .xlsx, .docx)
- **Behavior**: Prioritized, stealthy
- **Output**: Files renamed with .ryk extension

```bash
python simulator/malicious/ryuk_sim.py test-folder/ --speed 5 --algorithm aes256
```

#### 3. LockBit Simulator
- **Speed**: 100 files/second (TARGETED)
- **Targets**: Business-critical files (.xlsx, .sql, .bak, .docx)
- **Behavior**: Selective, focused
- **Output**: Files renamed with .lockbit extension

```bash
python simulator/malicious/lockbit_sim.py test-folder/ --speed 100 --algorithm fernet
```

---

### Benign Simulators

#### 1. Backup Simulator
- **Activity**: ZIP compression (7-Zip/WinRAR style)
- **Speed**: 50 files/second
- **Behavior**: Creates archive, does NOT modify originals
- **Expected**: NO EPA alert

```bash
python simulator/benign/backup_sim.py test-folder/ --speed 50
```

#### 2. Database Simulator
- **Activity**: SQLite database writes
- **Speed**: 50 operations/second
- **Behavior**: Writes encrypted data to .db file
- **Expected**: NO EPA alert

```bash
python simulator/benign/database_sim.py test-folder/ --operations 100 --speed 50
```

#### 3. Video Simulator
- **Activity**: Video encoding (MP4 compression)
- **Speed**: 1 video/minute
- **Behavior**: Creates compressed video files
- **Expected**: NO EPA alert

```bash
python simulator/benign/video_sim.py test-folder/ --count 3 --speed 1
```

---

## ✅ Testing Workflow

### Complete Test Sequence

```bash
# 1. Clean and prepare
rm -rf test-folder/
python simulator/generate_test_data.py test-folder/

# 2. Start EPA
python main.py &
cd dashboard && streamlit run app.py &

# 3. Test malicious attacks
python simulator/malicious/wannacry_sim.py test-folder/
# → Check dashboard for IMMEDIATE alert

# 4. Reset test data
python simulator/generate_test_data.py test-folder/ --clean

# 5. Test slow attack
python simulator/malicious/ryuk_sim.py test-folder/
# → Check dashboard for DELAYED alert (CUSUM)

# 6. Reset test data
python simulator/generate_test_data.py test-folder/ --clean

# 7. Test benign activity
python simulator/benign/backup_sim.py test-folder/
# → Check dashboard for NO alert (false positive test)
```

---

## 📈 Expected Results

| Simulation | Detection Expected | Detection Method | Latency |
|------------|-------------------|------------------|---------|
| WannaCry | ✅ Yes | Z-score | <10 seconds |
| Ryuk | ✅ Yes | CUSUM | <5 minutes |
| LockBit | ✅ Yes | Z-score | <10 seconds |
| Backup | ❌ No | N/A | N/A |
| Database | ❌ No | N/A | N/A |
| Video | ❌ No | N/A | N/A |

---

## 🔧 Customization

### Custom Attack Speed

```bash
# Very fast attack (1000 files/sec)
python simulator/malicious/wannacry_sim.py test-folder/ --speed 1000

# Very slow attack (1 file/min)
python simulator/malicious/ryuk_sim.py test-folder/ --speed 1
```

### Custom Encryption Algorithm

```bash
# Use AES-256
python simulator/malicious/wannacry_sim.py test-folder/ --algorithm aes256

# Use ChaCha20
python simulator/malicious/lockbit_sim.py test-folder/ --algorithm chacha20
```

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd /home/gautam/Desktop/Gautam/projects/personal/EPA

# Install dependencies
pip install cryptography
```

### No Files Found
```bash
# Generate test data first
python simulator/generate_test_data.py test-folder/
```

### EPA Not Detecting
- Check that EPA is running (`python main.py`)
- Check dashboard for alerts
- Verify `config.yaml` watch path matches test folder
- Check entropy threshold in `config.yaml`

---

## 📝 Notes

- **Always test in isolated folders** (e.g., `test-folder/`)
- **Backup important data** before running simulations
- **These are simulations** - files can be restored from backup
- **Monitor EPA dashboard** during simulations for real-time detection

---

## 🎓 Next Steps

1. Run all 6 simulations
2. Document detection results
3. Calculate detection accuracy and false positive rate
4. Tune EPA thresholds if needed
5. Iterate and improve detection algorithms

---

**Happy Testing! 🛡️**
