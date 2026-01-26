#!/bin/bash
# EPA Runner Script - Use the virtual environment Python

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️  EPA Ransomware Detection System${NC}"
echo "=========================================="

# Use venv Python
PYTHON="./venv/bin/python"

# Run EPA
echo -e "${GREEN}Starting EPA monitoring...${NC}"
$PYTHON main.py
