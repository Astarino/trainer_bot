# Fitness Trainer Web Application

A comprehensive fitness tracking web application built with FastAPI (Python) backend and React (TypeScript) frontend.

## 🏋️ Features

- **User Authentication** - JWT-based secure authentication system
- **Workout Programs** - Create and manage custom training programs
- **Exercise Library** - Comprehensive database of exercises with muscle groups and equipment
- **Workout Logging** - Track sets, reps, weight, RPE, and other metrics
- **Personal Records** - Automatic PR detection and tracking
- **Progress Visualization** - Charts and analytics for tracking fitness progress
- **User Profiles** - Personalized profiles with goals and preferences

## 📚 Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Database:** SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Authentication:** JWT tokens with bcrypt password hashing
- **Validation:** Pydantic schemas
- **Testing:** pytest

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **State Management:** Zustand
- **Data Fetching:** TanStack Query (React Query)
- **Forms:** React Hook Form + Zod validation
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Charts:** Chart.js with react-chartjs-2

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your configuration:
   ```env
   JWT_SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./trainer.db
   FRONTEND_URL=http://localhost:5173
   ```

   > **Important:** Generate a secure JWT secret key:
   > ```bash
   > openssl rand -hex 32
   > ```

5. **Run database migrations (if using Alembic):**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` if needed:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 📖 Development

### Backend Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/integration/test_auth.py -v

# Format code
black .

# Lint code
flake8

# Type checking
mypy backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## 🏗️ Project Structure

### Backend
```
backend/
├── models/          # SQLAlchemy database models
│   ├── mixins.py   # Reusable model mixins (timestamps, soft delete)
│   ├── user.py     # User model
│   ├── exercise.py # Exercise model
│   └── ...
├── routes/          # API endpoints (controllers)
│   └── auth.py     # Authentication routes
├── services/        # Business logic layer
├── repositories/    # Data access layer
├── schemas/         # Pydantic request/response schemas
├── utils/           # Helper functions (auth, etc.)
├── migrations/      # Alembic database migrations
├── tests/           # Test suite
├── config.py        # Configuration settings
├── database.py      # Database connection
└── main.py          # FastAPI application entry point
```

### Frontend
```
frontend/src/
├── assets/          # Static assets
├── components/      # Reusable UI components
├── pages/           # Route-level page components
│   ├── Auth/       # Login, Register pages
│   └── Dashboard/  # Dashboard page
├── hooks/           # Custom React hooks
├── services/        # API client and services
│   └── api.ts      # Axios client with interceptors
├── stores/          # Zustand state stores
│   └── authStore.ts # Authentication state
├── types/           # TypeScript type definitions
├── utils/           # Helper functions
├── constants/       # App constants
├── App.tsx          # Main App component
└── main.tsx         # Application entry point
```

## 🔒 Security Features

- **Password Hashing:** bcrypt with configurable rounds
- **JWT Tokens:** Short-lived access tokens (15 min) + refresh tokens (7 days)
- **Input Validation:** Pydantic schemas with strict validation
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **XSS Prevention:** React's built-in escaping + DOMPurify for HTML
- **CORS:** Configured for specific frontend origin
- **Security Headers:** X-Frame-Options, X-Content-Type-Options, HSTS
- **Rate Limiting:** Configured on authentication endpoints

## 📝 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Key Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=backend           # Run with coverage
pytest tests/unit/             # Run unit tests only
pytest tests/integration/      # Run integration tests only
pytest -k "test_auth"          # Run specific tests
```

### Frontend Tests

```bash
cd frontend
npm test                       # Run all tests
npm test -- --coverage        # Run with coverage
```

## 🚀 Deployment

### Backend Deployment

1. Set `DEBUG=false` in production
2. Use PostgreSQL instead of SQLite
3. Run with gunicorn or uvicorn workers:
   ```bash
   gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```
4. Set up database backups
5. Configure environment variables on hosting platform
6. Run migrations before deployment

### Frontend Deployment

1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Deploy the `dist/` directory to:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Or any static hosting service

## 📚 Documentation

- **CLAUDE.md** - Comprehensive development guide with architecture patterns, security best practices, and coding standards
- **todo.md** - Complete development roadmap with ~180 tasks across 9 phases

## 🎯 Development Roadmap

See `todo.md` for the complete development roadmap covering:
1. Project Setup & Infrastructure
2. Database Design & Models ✅
3. User Authentication ✅
4. Core Backend API
5. Frontend Development
6. Data Visualization
7. Testing & Quality Assurance
8. Deployment & DevOps
9. Future Enhancements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Commit Message Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code refactoring
- `docs:` Documentation changes
- `test:` Adding tests

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [React](https://react.dev/)
- Database ORM by [SQLAlchemy](https://www.sqlalchemy.org/)
- State management by [Zustand](https://github.com/pmndrs/zustand)

---

**Built with ❤️ for fitness enthusiasts**
