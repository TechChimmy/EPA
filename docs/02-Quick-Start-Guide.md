# EPA Quick Usage Guide

## 🚀 Getting Started

### 1. First Time Setup
```bash
# Run automated setup
bash setup.sh
```

### 2. Running EPA System

**Terminal 1: Start EPA Monitoring**
```bash
source venv/bin/activate
python main.py
```

**Terminal 2: Start Dashboard**
```bash
source venv/bin/activate
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

### Malicious Attacks (Should Detect)
```bash
source venv/bin/activate

# WannaCry-style (fast)
python simulator/malicious/wannacry_sim.py test-folder/

# Ryuk-style (slow)
python simulator/malicious/ryuk_sim.py test-folder/

# LockBit-style (targeted)
python simulator/malicious/lockbit_sim.py test-folder/
```

### Benign Activities (Should NOT Detect)
```bash
source venv/bin/activate

# Backup
python simulator/benign/backup_sim.py test-folder/

# Database
python simulator/benign/database_sim.py test-folder/

# Video
python simulator/benign/video_sim.py test-folder/
```

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
