# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack solar PV modeling application with:
- **Backend**: Django REST API with solar calculation engine using pvlib
- **Frontend**: React TypeScript with OpenLayers mapping and Vite
- **Deployment**: Docker Compose for development, Kubernetes for production
- **Testing**: pytest for backend, ESLint for frontend code quality

## Architecture

### Backend (Django)
- **Core Module**: `aerialytic/pv_modeling/optimal_orientation.py` - Solar geometry calculations using pvlib
- **API Endpoints**: `aerialytic/views.py` - REST endpoints for solar calculations
- **Settings**: `aerialytic/settings.py` - Django configuration with CORS, database, and REST framework
- **Testing**: `aerialytic/tests/` - pytest tests with Django integration
- **Production Deployment**: Uses Gunicorn WSGI server with production Dockerfile (`Dockerfile.backend.prod`)

### Frontend (React TypeScript)
- **Main Component**: `frontend/src/SolarGeometry.tsx` - Interactive map and solar calculation interface
- **Build Tool**: Vite with TypeScript and React plugins
- **Mapping**: OpenLayers (ol) for interactive location selection
- **Styling**: CSS modules with responsive design

### Key Solar Calculation Features
- Optimal tilt and azimuth calculation for maximum annual irradiance
- Ground slope compensation for accurate orientation on sloped terrain
- Liu and Jordan model for irradiance on tilted surfaces
- Clear Sky model (Ineichen-Perez) for atmospheric effects
- Annual energy optimization algorithms

## Common Development Commands

### Backend Development
```bash
# Run tests
pytest

# Run tests in Docker
docker compose exec backend pytest

# Run specific test file
pytest aerialytic/tests/test_optimal_orientation.py

# Django management commands (in Docker)
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### Frontend Development
```bash
# Frontend commands (run from frontend/ directory)
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build

# TypeScript type checking
cd frontend && npx tsc --noEmit
```

### Full Stack Development
```bash
# Run entire stack with Docker Compose
./deploy.sh dev

# Build and install dependencies locally (for linting/IDE support)
./setup.sh

# Root package.json scripts (for local development without Docker)
npm run dev          # Run both backend and frontend concurrently
npm run backend      # Run Django server on localhost:8001
npm run frontend     # Run Vite dev server on localhost:5174
npm run install-deps # Install both Python and Node dependencies
npm run build        # Build frontend
```

### Database Operations
```bash
# Access PostgreSQL in Docker
docker compose exec db psql -U aerialytic_user -d aerialytic

# Run migrations
docker compose exec backend python manage.py migrate
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes (Minikube) - Production Mode
./deploy_k8s.sh deploy

# Remove from Kubernetes
./deploy_k8s.sh undeploy

# Scale deployments
kubectl scale deployment backend-deployment --replicas=2
kubectl scale deployment frontend-deployment --replicas=2
```

## Environment Configuration

Required environment variables (create `.env` file):
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
DATABASE_URL=postgresql://aerialytic_user:aerialytic_password@db:5432/aerialytic
VITE_API_URL=http://localhost:8001
```

## Code Architecture Notes

### Solar Calculation Engine
- Uses pvlib library for scientifically accurate solar modeling
- Implements multiple solar radiation models (Liu & Jordan, Perez, Clear Sky)
- Ground slope compensation for terrain-aware calculations
- Time zone handling based on longitude coordinates
- Optimization algorithms for finding optimal panel orientation

### API Design
- Django REST Framework with CORS enabled for frontend integration
- Single endpoint `/api/optimal-orientation/` for solar calculations
- JSON request/response format with latitude, longitude, and ground slope parameters
- Error handling for invalid coordinates and calculation failures

### Frontend Architecture
- React functional components with TypeScript
- OpenLayers integration for interactive map-based location selection
- State management using React hooks
- API integration with error handling and loading states
- Responsive design for desktop and mobile use

### Testing Strategy
- Backend: pytest with Django integration, fixtures in `conftest.py`
- Test coverage for solar calculation algorithms and API endpoints
- Docker-based testing environment for consistency
- Frontend: ESLint for code quality (testing framework not yet implemented)

## Production Configuration

### Kubernetes Backend Production Features
- **DEBUG=False** for production security
- **Gunicorn WSGI server** instead of Django development server
- **Kubernetes Secrets** for sensitive configuration (SECRET_KEY)
- **Resource limits** and **health checks** (liveness/readiness probes)
- **Restricted CORS** origins for security
- **Non-root container user** for enhanced security
- **Static file collection** for proper asset serving

### Production Deployment Files
- `Dockerfile.backend.prod` - Production backend container with Gunicorn
- `k8s-backend-deployment.yaml` - Production Kubernetes configuration with secrets and health checks
- `deploy_k8s.sh` - Deployment script using production images

### Security Notes
- Change the SECRET_KEY in the Kubernetes Secret before production use
- Update CORS_ALLOWED_ORIGINS to match your actual frontend URLs
- Consider using external secret management (e.g., Vault) for production secrets

## Development Workflow

1. **Local Setup**: Run `./setup.sh` to install dependencies for linting and IDE support
2. **Development**: Use `./deploy.sh dev` for full Docker stack or root `npm run dev` for local development
3. **Testing**: Always run `pytest` before committing backend changes
4. **Code Quality**: Run `cd frontend && npm run lint` for frontend code quality checks
5. **Building**: Use `npm run build` (root) or `cd frontend && npm run build` for production builds
6. **Production Deployment**: Use `./deploy_k8s.sh deploy` for production-ready Kubernetes deployment

## Important File Locations

- Solar calculation logic: `aerialytic/pv_modeling/optimal_orientation.py`
- API endpoints: `aerialytic/views.py`
- Frontend main component: `frontend/src/SolarGeometry.tsx`
- Backend tests: `aerialytic/tests/`
- Configuration: `aerialytic/settings.py`, `frontend/vite.config.ts`
- Documentation: `aerialytic/pv_modeling/solar_formulas.md`