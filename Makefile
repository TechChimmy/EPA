# EPA Project Makefile

.PHONY: help run setup clean test wannacry lockbit ryuk

help:
	@echo "EPA Project Management Commands:"
	@echo "  make run      - Start both EPA monitor and Streamlit dashboard"
	@echo "  make setup    - Install dependencies and setup environment"
	@echo "  make clean    - Clear database and reset test folder"
	@echo "  make test     - Run all tests"
	@echo "  make wannacry - Run WannaCry attack simulation (test-folder/)"
	@echo "  make lockbit  - Run LockBit attack simulation (test-folder/)"
	@echo "  make ryuk     - Run Ryuk attack simulation (test-folder/)"

run:
	@echo "🚀 Starting EPA Monitor and Dashboard..."
	@# Run monitor in background and start dashboard
	./venv/bin/python3 main.py & ./venv/bin/streamlit run dashboard/app.py

setup:
	@echo "⚙️ Setting up environment..."
	bash setup.sh

clean:
	@echo "🧹 Cleaning environment..."
	rm -f epa.db
	./venv/bin/python3 simulator/generate_test_data.py test-folder --clean

test:
	@echo "🧪 Running tests..."
	bash run_tests.sh

wannacry:
	@echo "👹 Running WannaCry Simulation..."
	./venv/bin/python3 simulator/malicious/wannacry_sim.py test-folder --speed 50 --algorithm aes256

lockbit:
	@echo "👹 Running LockBit Simulation..."
	./venv/bin/python3 simulator/malicious/lockbit_sim.py test-folder --speed 50 --algorithm fernet

ryuk:
	@echo "👹 Running Ryuk Simulation..."
	./venv/bin/python3 simulator/malicious/ryuk_sim.py test-folder --speed 50 --algorithm aes256
