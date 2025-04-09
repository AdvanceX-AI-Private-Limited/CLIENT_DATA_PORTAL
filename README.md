# User-Outlet-Service Mapping Platform

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

A modern web application built with FastAPI backend and Vue.js frontend with Tailwind CSS for styling, designed to manage relationships between users, outlets, and services.

## Features

- **User Management**: Create, read, update, and delete user accounts
- **Outlet Management**: Manage physical/digital outlets and their attributes
- **Service Mapping**: Associate services with specific outlets and users
- **Role-Based Access Control**: Different permission levels for different user types
- **RESTful API**: Clean, well-documented API endpoints
- **Responsive UI**: Mobile-friendly interface built with Vue.js and Tailwind CSS

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: Automatic Swagger UI and ReDoc

### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **HTTP Client**: Axios

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- pipenv (for Python virtual environment)
- npm or yarn

## Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AdvanceX-AI-Private-Limited/CLIENT_DATA_PORTAL.git
   ```

2. Create and activate virtual environment:
   ```bash
    cd CLIENT_DATA_PORTAL/backend
    python -m venv venv
    venv/Scripts/Activate
    pip install -r ./requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your database credentials and other settings.

4. Start the FastAPI server:
   ```bash
   python ./main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
.
├── backend                # FastAPI backend/
│   ├── api/
│   │   └── v1             # Version Control/
│   │       ├── routers/    # API routes
│   │       ├── database/         # Database models and sessions
│   │       ├── schemas/    # Pydantic models
│   │       └── utils/      # Business logic
│   └── tests/              # Test cases
│
└── frontend/               # Vue.js frontend
    ├── public/             # Static assets
    ├── src/                # Application source
    │   ├── assets/         # Compiled assets
    │   ├── components/     # Vue components
    │   ├── router/         # Vue Router configuration
    │   ├── stores/         # Pinia stores
    │   └── views/          # Page components
    └── vite.config.js      # Tailwind configuration
```

## API Documentation

After starting the backend server, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

