# Aerialytic Technical Assignment

A fullstack application with Django backend and React TypeScript frontend.

## Project Structure

```
aerialytic-technical-assignment/
├── aerialytic/          # Django project
├── frontend/           # React TypeScript frontend
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies and scripts
├── run_dev.sh         # Shell script to run both servers
├── dev_utils.sh       # Development utilities for port management
└── README.md          # This file
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm

## Quick Start

### Option 1: Using the Shell Script (Recommended)

```bash
# Make the script executable (if not already)
chmod +x run_dev.sh

# Run both Django and React servers
./run_dev.sh
```

This script will:
- Check for and resolve port conflicts automatically
- Create a virtual environment if it doesn't exist
- Install Python dependencies
- Install Node.js dependencies
- Start Django server on http://192.168.1.102:8001
- Start React development server on http://192.168.1.102:5174

### Option 2: Using npm Scripts

```bash
# Install all dependencies
npm run install-deps

# Start both servers
npm run dev
```

### Option 3: Manual Setup

```bash
# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 192.168.1.102:8001

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5174
```

## Development Utilities

The project includes a utility script for managing development processes:

```bash
# Make the utility script executable
chmod +x dev_utils.sh

# Check status of development servers
./dev_utils.sh status

# Kill processes on development ports (8001, 5174)
./dev_utils.sh kill-ports

# Clean up all development processes
./dev_utils.sh clean

# Restart the entire development environment
./dev_utils.sh restart
```

## Available Scripts

### Root Directory (npm scripts)
- `npm run dev` - Start both Django and React servers
- `npm run backend` - Start only Django server
- `npm run frontend` - Start only React development server
- `npm run install-deps` - Install all dependencies
- `npm run build` - Build React frontend for production

### Frontend Directory
- `npm run dev` - Start React development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Development

### Django Backend
- Server runs on http://192.168.1.102:8001
- API endpoints can be accessed at http://192.168.1.102:8001/api/
- Django admin at http://192.168.1.102:8001/admin/

### React Frontend
- Development server runs on http://192.168.1.102:5174
- Hot reload enabled for development
- TypeScript support with strict type checking
- Accessible from other machines on the network

## Network Configuration

Both Django and React are configured to run on the network interface `192.168.1.102`:

- **Django**: Binds to `0.0.0.0:8001` (accessible on 192.168.1.102:8001)
- **React**: Binds to `0.0.0.0:5174` (accessible on 192.168.1.102:5174)

CORS is configured to allow communication between the frontend and backend on the same server.

## Stopping the Servers

- **Shell script**: Press `Ctrl+C` to stop both servers
- **npm scripts**: Press `Ctrl+C` to stop both servers
- **Manual**: Stop each server individually with `Ctrl+C`

## Troubleshooting

### Port Already in Use Error

If you encounter "port already in use" errors:

1. **Use the utility script** (recommended):
   ```bash
   ./dev_utils.sh kill-ports
   ```

2. **Manual port cleanup**:
   ```bash
   # Kill Django port
   sudo lsof -ti :8001 | xargs kill -9
   
   # Kill React port
   sudo lsof -ti :5174 | xargs kill -9
   ```

3. **Check what's using the ports**:
   ```bash
   lsof -i :8001
   lsof -i :5174
   ```

### Virtual Environment Issues

If you have virtual environment problems:

```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues

If you have frontend dependency issues:

```bash
# Clean and reinstall node modules
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Network Access Issues

If you can't access the servers from other machines:

1. **Check firewall settings**:
   ```bash
   sudo ufw status
   sudo ufw allow 8001
   sudo ufw allow 5174
   ```

2. **Verify server binding**:
   ```bash
   netstat -tlnp | grep :8001
   netstat -tlnp | grep :5174
   ```

## Production Build

```bash
# Build the React frontend
npm run build

# The built files will be in frontend/dist/
```

## Technologies Used

### Backend
- Django 5.2.3
- Django REST Framework 3.14.0
- Django CORS Headers 4.3.1
- Python Decouple 3.8
- Pillow 10.1.0

### Frontend
- React 19.1.0
- TypeScript 5.8.3
- Vite 6.3.5
- ESLint 9.25.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## License

MIT License