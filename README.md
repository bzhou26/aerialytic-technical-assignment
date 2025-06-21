# Aerialytic Technical Assignment

A fullstack application with Django backend and React TypeScript frontend, fully containerized with Docker.

## Project Structure

```
aerialytic-technical-assignment/
├── aerialytic/         # Django project
├── frontend/           # React TypeScript frontend
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies and scripts
├── setup.sh            # Environment setup script (pyenv, npm)
├── docker-compose.yml  # Docker Compose configuration (includes override)
├── Dockerfile.backend  # Django backend Dockerfile
├── frontend/Dockerfile.frontend # React frontend Dockerfile
├── deploy.sh           # Docker deployment script
├── deploy_k8s.sh       # Kubernetes deployment script
└── README.md           # This file
```

## Documentation

### Solar Calculation Models
The solar geometry calculations are based on well-established mathematical models. For detailed information about the formulas and models used, see:
- [Solar Formulas Documentation](aerialytic/pv_modeling/solar_formulas.md) - Comprehensive documentation of mathematical models, including:
  - Solar position calculations (declination, hour angle, zenith angle, azimuth)
  - Liu and Jordan model for irradiance on tilted surfaces
  - Clear Sky model (Ineichen-Perez) for atmospheric effects
  - Ground slope compensation formulas
  - Annual energy optimization algorithms

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- npm
- pyenv & pyenv-virtualenv (for Python environment management)
- kubectl (for Kubernetes deployment)
- minikube (for local Kubernetes cluster)

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

## Database - connects to the db service started with Docker
DATABASE_URL=postgresql://aerialytic_user:aerialytic_password@db:5432/aerialytic


## Kubernetes Deployment

### Prerequisites
- Docker images for frontend and backend are built and pushed to a container registry accessible by your cluster (for Minikube, images are loaded locally).
- `kubectl` and `minikube` are installed and configured.

### Minikube Configuration
```bash
minikube start
kubectl config use-context minikube
```

### Deployment Script
```bash
chmod +x deploy_k8s.sh
```

### Deploy All Services to Kubernetes

```bash
./deploy_k8s.sh deploy
```
This will:
- Build and load Docker images for backend and frontend into Minikube
- Deploy the PostgreSQL database, backend, and frontend
- Wait for the database to be ready before deploying the backend
- Show the status of all pods and services

### Undeploy All Services from Kubernetes

```bash
./deploy_k8s.sh undeploy
```
This will delete all Kubernetes resources for this project (frontend, backend, and database).

### Usage
```bash
# Show usage information
./deploy_k8s.sh

# Deploy the application
./deploy_k8s.sh deploy

# Remove the application
./deploy_k8s.sh undeploy
```

### Scaling Deployments
To scale the backend or frontend, use:
```sh
kubectl scale deployment backend-deployment --replicas=2
kubectl scale deployment frontend-deployment --replicas=2
```
Replace `2` with your desired number of replicas.

### Accessing Services
- By default, services are exposed via LoadBalancer.
- To access from your host machine (localhost), run `minikube tunnel`.
- To expose services to other devices on your local network, you must bind the tunnel to your host's LAN IP. Find your IP with `hostname -I`, then run:
  ```sh
  sudo minikube tunnel --bind-address=0.0.0.0
  ```
  You can then access the services at `http://<your-lan-ip>:<service-port>`.

## TODO
Due to the time, here are a list of items can be added to the system to improve both user experience and development experience.

### Features to optimize PV modeling
- [ ] **Weather Data Integration**: Integrate real weather data APIs for more accurate solar calculations
- [ ] **Historical Data Analysis**: Add functionality to analyze historical solar performance data
- [ ] **Multiple Panel Types**: Support for different solar panel technologies and specifications
- [ ] **Shading Analysis**: Implement shading analysis to account for nearby obstacles
- [ ] **Higher Resolution Solar Data**: Increase solar data resolution from 5° to 1° or 0.5° for more precise calculations
- [ ] **Machine Learning Models**: Implement ML models to predict solar radiation based on historical patterns
- [ ] **Real-time Data**: Add real-time solar radiation data from weather APIs

### Features to add for the web application
- [ ] **Export Functionality**: Allow users to export calculation results to PDF/Excel
- [ ] **User Authentication**: Add user accounts and save calculation history
- [ ] **Mobile App**: Develop a mobile application for on-site solar assessments
- [ ] **Performance Optimization**: Optimize solar calculations for faster response times
- [ ] **Caching**: Implement caching for frequently requested calculations
- [ ] **API Rate Limiting**: Add rate limiting to prevent API abuse
- [ ] **Database Support**: Add database support to the system
- [ ] **Error Handling**: Improve error handling and user feedback
- [ ] **Logging**: Add comprehensive logging for debugging and monitoring
- [ ] **Monitoring**: Add health checks and monitoring endpoints
- [ ] **Security**: Implement additional security measures (input validation, CORS, etc.)

### Testing & Quality
- [ ] **Integration Tests**: Add end-to-end integration tests
- [ ] **Performance Tests**: Add load testing and performance benchmarks
- [ ] **Frontend Tests**: Add comprehensive frontend tests using Jest and React Testing Library
- [ ] **Error Boundary Tests**: Add tests for error boundaries and error handling
- [ ] **Form Validation Tests**: Add tests for form validation and user interactions
- [ ] **Coverage**: Keep test coverage to >90%
- [ ] **Code Quality**: Add linting rules and code quality checks
- [ ] **Documentation**: Add API documentation (Swagger/OpenAPI)
- [ ] **User Guide**: Create comprehensive user documentation

### Infrastructure & DevOps
- [ ] **CI/CD Pipeline**: Set up automated testing and deployment pipelines
- [ ] **Container Registry**: Use a proper container registry instead of local images
- [ ] **Environment Management**: Add staging and production environment configurations
- [ ] **Backup Strategy**: Implement database backup and recovery procedures
- [ ] **SSL/TLS**: Add proper SSL certificates for production deployment
- [ ] **Load Balancer**: Implement load balancing Nginx for high availability
- [ ] **Auto-scaling**: Add auto-scaling capabilities for Kubernetes deployment

### UI/UX Improvements
- [ ] **Responsive Design**: Improve mobile responsiveness with Tailwind CSS breakpoints and responsive utilities
- [ ] **Interactive Maps**: Add interactive map selection for location picking with Leaflet.js and custom Tailwind styling
- [ ] **Google Maps Integration**: Replace open-source maps with Google Maps API for enhanced location services, street view, and satellite imagery with custom Tailwind CSS styling for map controls and overlays
- [ ] **Visualizations**: Add charts and graphs for solar data visualization using Chart.js with Tailwind CSS theming
- [ ] **Internationalization**: Add multi-language support with react-i18next and Tailwind CSS RTL support
- [ ] **Loading States**: Add skeleton loaders and loading animations using Tailwind CSS animation classes
- [ ] **Icon Integration**: Integrate heroicons or custom SVG icons with Tailwind CSS sizing and color utilities
- [ ] **Toast Notifications**: Create toast notification system with Tailwind CSS positioning and animation classes

### Development Environment Improvements
- [ ] **Hot Reloading**: Configure hot reloading for both frontend and backend development
- [ ] **Development Tools**: Add development tools like React DevTools and Django Debug Toolbar
- [ ] **Code Formatting**: Set up Ruff for consistent code formatting
- [ ] **Pre-commit Hooks**: Add pre-commit hooks for linting and formatting
- [ ] **IDE Configuration**: Add VS Code settings and extensions recommendations
- [ ] **Environment Variables**: Set up proper environment variable management for different environments
- [ ] **Mock Data**: Add mock data generators for development and testing
- [ ] **Development Scripts**: Add convenient npm scripts for common development tasks
- [ ] **Debugging Setup**: Configure debugging for both frontend and backend
- [ ] **Type Checking**: Set up TypeScript strict mode and type checking in CI
- [ ] **Code Generation**: Add code generators for common patterns (components, models, etc.)
- [ ] **Documentation Generation**: Set up automatic API documentation generation

### Project Configuration Improvements
- [ ] **Dependency Management**: Use pyproject.toml for dependency specification and version management
- [ ] **Development Dependencies**: Separate development dependencies from production dependencies
- [ ] **Optional Dependencies**: Configure optional dependencies for different deployment scenarios
- [ ] **Package Metadata**: Define package metadata, classifiers, and project information
- [ ] **Entry Points**: Configure console scripts and entry points
- [ ] **Multi-environment**: Support multiple Python versions and environments
- [ ] **Dependency Locking**: Implement dependency locking for reproducible builds
