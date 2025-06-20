#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PYTHON_VERSION="3.11.9"
VIRTUALENV_NAME="aerialytic"

# Check for pyenv
if ! command -v pyenv &> /dev/null; then
    echo -e "${RED}pyenv is not installed!${NC}"
    echo -e "${YELLOW}Please install pyenv and pyenv-virtualenv, then restart your shell.${NC}"
    exit 1
fi

# Check for pyenv-virtualenv
if ! pyenv virtualenvs --bare | grep -q "^${VIRTUALENV_NAME}$"; then
    if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
        echo -e "${YELLOW}Python ${PYTHON_VERSION} is not installed via pyenv. Installing...${NC}"
        pyenv install ${PYTHON_VERSION}
    fi
    echo -e "${YELLOW}Creating pyenv virtualenv '${VIRTUALENV_NAME}' with Python ${PYTHON_VERSION}...${NC}"
    pyenv virtualenv ${PYTHON_VERSION} ${VIRTUALENV_NAME}
fi

pyenv local ${VIRTUALENV_NAME}

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pyenv exec pip install -r requirements.txt

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed!${NC}"
    echo -e "${YELLOW}Please install Node.js and npm.${NC}"
    exit 1
fi

# Install frontend dependencies if needed
cd frontend
if [ ! -d node_modules ] || [ ! -f package-lock.json ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}Frontend dependencies already installed.${NC}"
fi
cd ..

echo -e "${GREEN}Environment setup complete!${NC}" 