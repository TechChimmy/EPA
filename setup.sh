#!/bin/bash
# EPA Setup Script - Automated installation and configuration

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}║   EPA - Entropy-based Process Anomaly Detection       ║${NC}"
echo -e "${BLUE}║   Setup Script                                         ║${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/6]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Create virtual environment
echo -e "${YELLOW}[2/6]${NC} Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC}  Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo -e "${YELLOW}[3/6]${NC} Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}[4/6]${NC} Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Initialize database
echo -e "${YELLOW}[5/6]${NC} Initializing database..."
python3 -c "from shared.db import init_db; init_db()"
echo -e "${GREEN}✓${NC} Database initialized"

# Generate test data
echo -e "${YELLOW}[6/6]${NC} Generating test data..."
if [ -d "test-folder" ]; then
    echo -e "${YELLOW}⚠${NC}  test-folder already exists"
    read -p "Do you want to regenerate test data? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf test-folder
        python3 simulator/generate_test_data.py test-folder/
        echo -e "${GREEN}✓${NC} Test data regenerated"
    else
        echo -e "${YELLOW}⚠${NC}  Skipping test data generation"
    fi
else
    python3 simulator/generate_test_data.py test-folder/
    echo -e "${GREEN}✓${NC} Test data generated (140 files)"
fi

# Setup complete
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}║   ✅ EPA Setup Complete!                               ║${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Start EPA monitoring:"
echo -e "     ${YELLOW}source venv/bin/activate && python main.py${NC}"
echo ""
echo -e "  2. Start dashboard (in another terminal):"
echo -e "     ${YELLOW}source venv/bin/activate && cd dashboard && streamlit run app.py${NC}"
echo ""
echo -e "  3. Run a simulation (in another terminal):"
echo -e "     ${YELLOW}source venv/bin/activate && python simulator/malicious/wannacry_sim.py test-folder/${NC}"
echo ""
echo -e "${BLUE}For more information, see MVP_GUIDE.md${NC}"
echo ""
