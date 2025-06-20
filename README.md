# Aerialytic Technical Assignment

A fullstack application with Django backend and React TypeScript frontend, fully containerized with Docker.

## Project Structure

```
aerialytic-technical-assignment/
├── aerialytic/          # Django project
├── frontend/           # React TypeScript frontend
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies and scripts
├── setup.sh            # Environment setup script (pyenv, npm)
├── docker-compose.yml  # Docker Compose configuration (includes override)
├── Dockerfile.backend  # Django backend Dockerfile
├── frontend/Dockerfile.frontend # React frontend Dockerfile for production
├── frontend/Dockerfile.frontend.dev # React development Dockerfile
├── deploy.sh           # Docker deployment script
└── README.md           # This file
```

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- npm
- pyenv & pyenv-virtualenv (for Python environment management)

## Environment Setup (for development, linting, and builds)

Before running any Docker Compose services, you should set up your local environment for development tools (linting, building, etc). This does **not** run any servers locally.

### 1. Run the setup script

```bash
./setup.sh
```
This will:
- Ensure the correct Python version and virtualenv (using pyenv)
- Install Python dependencies
- Install frontend dependencies (npm)

### 2. (Optional) Manual steps
If you want to do the steps manually:
```bash
# Python (Backend)
pyenv install 3.11.9
pyenv virtualenv 3.11.9 aerialytic
pyenv local aerialytic
pip install -r requirements.txt

# Node.js (Frontend)
cd frontend
npm install
```

You can now use npm scripts for linting, building, etc.:
```bash
# Lint the frontend code
npm run lint

# Build the frontend for production
npm run build
```

## Running the Application (Docker Compose)

All server processes (Django, React, PostgreSQL) are run inside Docker containers.

### Start the Full Stack

```bash
# Build and start all services (development mode)
./deploy.sh dev

# For production mode
./deploy.sh prod
```

### Database Management (Docker)

```bash
# Access the PostgreSQL container
docker compose exec db psql -U aerialytic_user -d aerialytic

# Run Django migrations
docker compose exec backend python manage.py migrate

# Create a superuser
docker compose exec backend python manage.py createsuperuser
```

## Environment Variables

Create a `.env` file in the project root for Django and Docker Compose. Example:

```env
# Django Settings
DEBUG=True
SECRET_KEY=a-good-secret-key-for-local-dev
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5174,http://127.0.0.1:5174

# Frontend API URL (dynamic)
VITE_API_URL=http://localhost:8001

# Database - connects to the db service started with Docker
DATABASE_URL=postgresql://aerialytic_user:aerialytic_password@db:5432/aerialytic
```

# Django Settings
DEBUG=True
SECRET_KEY=a-good-secret-key-for-local-dev
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5174,http://127.0.0.1:5174

# Frontend API URL (dynamic)
VITE_API_URL=http://localhost:8001

# Database - connects to the db service started with Docker
DATABASE_URL=postgresql://aerialytic_user:aerialytic_password@db:5432/aerialytic