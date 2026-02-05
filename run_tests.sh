#!/bin/bash
# EPA Test Runner Script
# Runs all unit tests and generates coverage report

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}║   EPA - Test Suite Runner                             ║${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Install test dependencies if needed
echo -e "${BLUE}[1/4]${NC} Checking test dependencies..."
pip install -q coverage pytest 2>/dev/null || true
echo -e "${GREEN}✓${NC} Dependencies ready"

# Run unit tests
echo ""
echo -e "${BLUE}[2/4]${NC} Running unit tests..."
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python -m unittest discover -s tests -p "test_*.py" -v

if [ $? -eq 0 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓${NC} All tests passed!"
else
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗${NC} Some tests failed"
    exit 1
fi

# Generate coverage report
echo ""
echo -e "${BLUE}[3/4]${NC} Generating coverage report..."
coverage run -m unittest discover -s tests -p "test_*.py" > /dev/null 2>&1
coverage report -m

# Generate HTML coverage report
echo ""
echo -e "${BLUE}[4/4]${NC} Generating HTML coverage report..."
coverage html
echo -e "${GREEN}✓${NC} HTML report generated in htmlcov/"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}║   ✅ Test Suite Complete!                              ║${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Coverage report:${NC} htmlcov/index.html"
echo -e "${BLUE}To view:${NC} open htmlcov/index.html in your browser"
echo ""

# Clean up test databases
echo -e "${YELLOW}Cleaning up test databases...${NC}"
rm -f test_*.db
echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""
