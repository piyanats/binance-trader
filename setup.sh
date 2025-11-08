#!/bin/bash

# Binance Thailand Trading Bot - Setup Script
# This script creates a virtual environment and installs dependencies using uv

set -e  # Exit on error

echo "========================================"
echo "Binance Thailand Trading Bot - Setup"
echo "========================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.13 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Found Python ${PYTHON_VERSION}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment recreated"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Check if uv is installed
echo ""
echo "Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} uv is not installed. Installing uv..."

    # Install uv using pip
    pip install --quiet uv

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} uv installed successfully"
    else
        echo -e "${RED}✗${NC} Failed to install uv"
        echo "Falling back to pip..."
        pip install --upgrade pip
        pip install -r requirements.txt
        exit 0
    fi
else
    echo -e "${GREEN}✓${NC} uv is already installed"
fi

# Display uv version
UV_VERSION=$(uv --version)
echo "Using ${UV_VERSION}"

# Install dependencies using uv
echo ""
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencies installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${YELLOW}⚠${NC} Please edit .env file with your API keys and Slack webhook"
else
    echo -e "${YELLOW}⚠${NC} .env file already exists, skipping"
fi

# Initialize portfolio
echo ""
echo "Initializing portfolio..."
python initialize_portfolio.py

# Display next steps
echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "2. Edit .env file with your credentials:"
echo "   ${GREEN}nano .env${NC}"
echo ""
echo "3. Test your configuration:"
echo "   ${GREEN}python test_connection.py${NC}"
echo ""
echo "4. Run the trading bot:"
echo "   ${GREEN}python trading_bot.py${NC}"
echo ""
echo "For detailed instructions, see:"
echo "  - README.md for comprehensive documentation"
echo "  - QUICKSTART.md for quick start guide"
echo ""
