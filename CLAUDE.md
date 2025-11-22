# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Fitness/Workout Trainer web application** designed to help users track workouts, manage training programs, monitor progress, and visualize fitness data.

**Stack:**
- **Backend:** Python (FastAPI or Flask) with SQLAlchemy ORM
- **Frontend:** React with Vite or Vue 3
- **Database:** PostgreSQL (production) / SQLite (development)
- **Authentication:** JWT-based authentication with bcrypt password hashing

**Core Features:**
- User authentication and profile management
- Workout program creation and management
- Exercise library with filtering/search
- Workout session logging (sets, reps, weight, RPE)
- Progress tracking and personal records
- Data visualization (charts, analytics, progress trends)

---

## Architecture

### Layered Architecture (Strict Separation)

The application follows a three-tier architecture with strict separation of concerns:

**Controllers/Routes (routes/):**
- Handle HTTP request/response
- Validate request payloads (Pydantic models)
- Call service layer
- Never access database directly

**Services (services/):**
- Business logic and orchestration
- Transaction management
- Call repository layer
- Never access request/response objects directly

**Repositories (repositories/):**
- Database access abstraction
- Query building and execution
- CRUD operations
- Return domain models

**Example Flow:**
```python
# routes/sessions.py
@router.post("/sessions")
def create_session(session_data: WorkoutSessionCreate, user=Depends(get_current_user)):
    return session_service.create_session(user.id, session_data)

# services/session_service.py
class SessionService:
    def __init__(self, session_repo, pr_service):
        self.session_repo = session_repo
        self.pr_service = pr_service

    def create_session(self, user_id, session_data):
        with transaction():
            session = self.session_repo.create(user_id, session_data)
            self.pr_service.check_and_update_prs(session)
            return session

# repositories/session_repository.py
class SessionRepository:
    def create(self, user_id, session_data):
        return db.query(WorkoutSession).filter(...)
```

### Backend Structure
```
backend/
├── models/          # SQLAlchemy ORM models
├── routes/          # API endpoint definitions (controllers)
├── services/        # Business logic layer
├── repositories/    # Data access layer
├── schemas/         # Pydantic request/response schemas
├── utils/           # Helper functions, auth utilities
├── migrations/      # Alembic database migrations
└── config.py        # Environment-based configuration
```

### Frontend Structure
```
frontend/src/
├── assets/          # Images, fonts, global CSS
├── components/      # Reusable UI components
│   ├── Button/
│   ├── Forms/
│   └── Skeletons/
├── pages/           # Route-level page components
│   ├── Dashboard/
│   ├── Sessions/
│   └── Programs/
├── hooks/           # Custom React hooks
├── services/        # API client and data fetching
├── stores/          # State management (Zustand/Pinia)
├── types/           # TypeScript types
├── utils/           # Helper functions
└── constants/       # App constants
```

### Background Tasks

**Library:** Celery with Redis broker OR FastAPI BackgroundTasks for simple jobs

**Use Cases:**
- Email notifications (PR achievements, workout reminders)
- Weekly progress report generation
- Cleanup old sessions
- Recalculate aggregated statistics

### File Uploads

**Storage Strategy:**
- Profile Photos: S3/CloudStorage or local storage with 5MB size limit
- Exercise Videos: Video processing queue, thumbnail generation
- Path Pattern: `uploads/{user_id}/{type}/{filename}`
- Validation: File type, size limits, virus scanning

---

## Data Model

### Core Models

**Key Models:**
- `User` - Authentication and user data
- `Exercise` - Exercise library (name, muscle group, equipment)
- `WorkoutProgram` - User-created training programs
- `ProgramExercise` - Many-to-many join table with exercise prescription
- `WorkoutSession` - Individual workout instances
- `Set` - Individual set data (exercise, weight, reps, RPE)
- `UserProfile` - Extended user information (weight, goals)
- `PersonalRecord` - PR tracking per exercise

### Database Relationships
- `User` has many `WorkoutProgram`, `WorkoutSession`, `PersonalRecord`
- `User` has one `UserProfile`
- `WorkoutProgram` has many `ProgramExercise` (join table)
- `WorkoutSession` has many `Set`
- `Set` references `Exercise`
- `PersonalRecord` links `User`, `Exercise`, and the achieving `Set`

### Critical Modeling Principles

**1. Soft Deletes (MANDATORY for most models)**
```python
class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True, index=True)
    is_deleted = Column(Boolean, default=False, server_default='0', index=True)

# Apply to: User, WorkoutProgram, WorkoutSession, Exercise
# Hard delete only: Set (if parent deleted), JWT tokens
```

**2. Timestamp Tracking (ALL models)**
```python
class TimestampMixin:
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**3. Database Constraints**
```python
# Example: Set model
CheckConstraint('weight >= 0 AND weight <= 10000', name='weight_range')
CheckConstraint('reps >= 0 AND reps <= 1000', name='reps_range')
CheckConstraint('rpe IS NULL OR (rpe >= 1 AND rpe <= 10)', name='rpe_range')
```

**4. Indexing Strategy (Performance Critical)**
```python
# Foreign keys - Always indexed
Index('idx_session_user', WorkoutSession.user_id)

# Common query patterns - Composite indexes
Index('idx_session_user_date', WorkoutSession.user_id, WorkoutSession.session_date)
Index('idx_set_exercise_weight', Set.exercise_id, Set.weight.desc())  # For PR queries

# Soft delete filtering
Index('idx_exercise_active', Exercise.is_deleted, Exercise.primary_muscle_group)
```

**5. Critical: Unit Storage**
```python
# ALWAYS store the original unit with the value
class Set(Base):
    weight = Column(Numeric(6, 2), nullable=False)  # Use Decimal, not Float!
    weight_unit = Column(Enum('kg', 'lbs'), nullable=False)
```

---

## Development Commands

### Backend

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run development server
# FastAPI: uvicorn main:app --reload
# Flask: flask run --debug

# Run tests with coverage
pytest --cov=backend --cov-report=html --cov-report=term

# Run specific test
pytest tests/integration/test_session_endpoints.py -v

# Run tests matching pattern
pytest -k "test_pr" -v

# Code formatting and linting
black .
flake8

# Create database migration
alembic revision --autogenerate -m "description"

# Seed database
python scripts/seed_exercises.py
```

### Frontend

```bash
# Install dependencies
npm install  # or yarn install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
npm test -- ComponentName  # Single component

# Linting and formatting
npm run lint
npm run format

# Type checking
npm run type-check
```

---

## Security Best Practices

### Input Validation (MANDATORY)

**All API endpoints MUST use Pydantic models for validation:**
```python
from pydantic import BaseModel, Field, validator

class SetCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    weight: float = Field(ge=0, le=1000)
    reps: int = Field(ge=0, le=100)
    rpe: Optional[int] = Field(ge=1, le=10, default=None)

    @validator('weight')
    def validate_weight(cls, v):
        return round(v, 2)  # Prevent floating point issues
```

### Authentication Security

**JWT Token Strategy:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Longer-lived

# Store refresh tokens in httpOnly cookies
# Access tokens in memory (React state/Zustand)
# Implement token rotation on refresh
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 number
- Check against common password lists
- Always use bcrypt for hashing

### Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
def login(...):
    ...
```

### SQL Injection Prevention

```python
# NEVER use string formatting for queries
# WRONG: f"SELECT * FROM users WHERE username = '{username}'"

# CORRECT: Use ORM
db.query(User).filter(User.username == username).first()

# If raw SQL needed, use parameterized queries
db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
```

### XSS Prevention

**Backend:** Validate and sanitize all user inputs

**Frontend:**
```typescript
import DOMPurify from 'dompurify'

// Sanitize HTML before rendering
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(notes) }} />

// Or just render as text (React escapes automatically)
<div>{notes}</div>
```

### Security Headers

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

## API Design Standards

### Standard Response Formats

**Success Response (200, 201):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Push Day"
  },
  "meta": {
    "timestamp": "2025-01-22T10:30:00Z"
  }
}
```

**List Response with Pagination:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_items": 95,
    "has_next": true
  }
}
```

**Error Response (4xx, 5xx):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid workout data",
    "details": [
      {
        "field": "weight",
        "message": "Weight must be positive"
      }
    ]
  }
}
```

### HTTP Status Codes

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST (return created resource with Location header)
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation errors, malformed request
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but lacking permissions
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Business logic validation failure
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected errors (log details, return generic message)

### API Endpoint Patterns

- `/api/auth/*` - Authentication endpoints
- `/api/programs/*` - Workout program CRUD
- `/api/exercises/*` - Exercise library access
- `/api/sessions/*` - Workout session logging
- `/api/sessions/:id/sets/*` - Set operations within session
- `/api/progress/*` - Progress and analytics data
- `/api/profile/*` - User profile management

### Pagination and Filtering

```
GET /api/sessions?page=1&per_page=20&sort=-created_at&filter[exercise_id]=5

Parameters:
- page: Page number (1-indexed, default: 1)
- per_page: Items per page (default: 20, max: 100)
- sort: Field to sort (prefix - for descending)
- filter[field]: Filter by field value
- start_date/end_date: Date range filtering
```

### API Versioning

Use URL path versioning:
```
/api/v1/sessions
/api/v2/sessions  # Breaking changes
```

---

## Frontend Architecture

### State Management

**Recommended:** Zustand (React) or Pinia (Vue)

```typescript
// stores/authStore.ts
import create from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      login: async (email, password) => {
        const { data } = await api.post('/auth/login', { email, password })
        set({ user: data.user, accessToken: data.access_token, isAuthenticated: true })
      },
      logout: () => set({ user: null, accessToken: null, isAuthenticated: false })
    }),
    { name: 'auth-storage' }
  )
)
```

### Component Patterns

**Container/Presentational Pattern:**

```typescript
// WorkoutSessionContainer.tsx (Smart - handles data)
export const WorkoutSessionContainer: React.FC = ({ sessionId }) => {
  const { data, isLoading, error } = useQuery(['session', sessionId], fetchSession)
  const addSetMutation = useMutation(addSet)

  if (isLoading) return <Skeleton />
  if (error) return <ErrorAlert error={error} />

  return <WorkoutSessionView session={data} onAddSet={addSetMutation.mutate} />
}

// WorkoutSessionView.tsx (Dumb - only UI)
export const WorkoutSessionView: React.FC<Props> = ({ session, onAddSet }) => {
  return (
    <div>
      <h1>{session.name}</h1>
      <SetForm onSubmit={onAddSet} />
    </div>
  )
}
```

### Form Handling

**React Hook Form + Zod:**
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const setSchema = z.object({
  weight: z.number().min(0).max(1000),
  reps: z.number().int().min(0).max(100)
})

export const SetForm: React.FC = ({ onSubmit }) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(setSchema)
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('weight', { valueAsNumber: true })} />
      {errors.weight && <span>{errors.weight.message}</span>}
    </form>
  )
}
```

### API Client Pattern

```typescript
// services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
})

// Request interceptor - Add auth token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await refreshToken()
      return api(error.config)
    }
    return Promise.reject(error)
  }
)
```

### Error Handling

```typescript
// Global Error Boundary
export class ErrorBoundary extends Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error:', error, errorInfo)
    // Send to Sentry or error tracking service
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />
    }
    return this.props.children
  }
}
```

---

## Performance Optimization

### Backend Performance

**N+1 Query Prevention (CRITICAL):**
```python
# BAD - N+1 queries
sessions = db.query(WorkoutSession).all()
for session in sessions:
    sets = session.sets  # New query each iteration!

# GOOD - Eager loading
from sqlalchemy.orm import selectinload

sessions = db.query(WorkoutSession)\
    .options(selectinload(WorkoutSession.sets).joinedload(Set.exercise))\
    .all()
```

**Database Query Optimization:**
```python
# Use SELECT only needed columns
db.query(WorkoutSession.id, WorkoutSession.name).filter(...).all()

# Use database-level aggregations
total_volume = db.query(func.sum(Set.weight * Set.reps)).scalar()

# Batch operations
db.bulk_insert_mappings(Set, set_data_list)
```

**Caching Strategy (Redis):**
```python
@cache_result(expire_seconds=3600)
def get_exercise_library():
    return db.query(Exercise).filter(Exercise.is_deleted == False).all()

# Cache invalidation
def create_session(user_id, data):
    session = create(...)
    redis_client.delete(f"user_sessions:{user_id}")
    return session
```

**What to Cache:**
- Exercise library (24 hours)
- User PRs (1 hour)
- Aggregated statistics (30 minutes)

**What NOT to Cache:**
- Current workout session
- User authentication state

### Frontend Performance

**Code Splitting:**
```typescript
// Lazy load routes
const DashboardPage = lazy(() => import('@/pages/Dashboard'))

<Suspense fallback={<PageSkeleton />}>
  <DashboardPage />
</Suspense>
```

**React Query Caching:**
```typescript
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 minutes
      cacheTime: 10 * 60 * 1000  // 10 minutes
    }
  }
})
```

**Image Optimization:**
- Resize images before upload (max 800px)
- Use lazy loading for images
- Compress with quality 85%

**Debouncing:**
```typescript
export const useDebounce = <T,>(value: T, delay: number = 500): T => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}
```

---

## Common Pitfalls and Critical Gotchas

### 1. Timezone Handling (EXTREMELY IMPORTANT)

**ALWAYS store in UTC, display in user's local timezone:**

```python
# Backend - ALWAYS use UTC
from datetime import datetime, timezone

session.created_at = datetime.now(timezone.utc)  # CORRECT
session.created_at = datetime.now()  # WRONG - uses local time!
```

```typescript
// Frontend - Convert to user timezone for display
import { parseISO, format } from 'date-fns'

const sessionDate = parseISO(session.created_at)  // Parse UTC from API
format(sessionDate, 'PPpp')  // Display in user's local timezone
```

### 2. Unit Conversions and Floating Point Precision

**Use Decimal for weight calculations, not float:**

```python
from decimal import Decimal, ROUND_HALF_UP

KG_TO_LBS = Decimal('2.20462')

def convert_weight(weight: float, from_unit: str, to_unit: str) -> Decimal:
    weight_decimal = Decimal(str(weight))  # Convert to string first!
    result = weight_decimal * KG_TO_LBS
    return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# Database column
weight = Column(Numeric(6, 2), nullable=False)  # NOT Float!
```

### 3. Date vs DateTime Confusion

```python
# Use Date for session_date (no time component)
session_date = Column(Date, nullable=False)
session.session_date = date.today()

# Use DateTime for timestamps
created_at = Column(DateTime, nullable=False)
session.created_at = datetime.now(timezone.utc)

# Querying dates works correctly
sessions_today = db.query(WorkoutSession).filter(
    WorkoutSession.session_date == date.today()
).all()
```

### 4. Cascade Deletes - Data Loss Prevention

```python
# DANGEROUS - deleting user deletes all workout history
class User(Base):
    sessions = relationship("WorkoutSession", cascade="all, delete-orphan")

# SAFER - use soft deletes
class User(Base, SoftDeleteMixin):
    sessions = relationship("WorkoutSession")

def delete_user(user_id):
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()  # Data preserved
```

### 5. Race Conditions in PR Updates

```python
# Use database locking for concurrent PR updates
from sqlalchemy import select

current_pr = db.execute(
    select(PersonalRecord)
    .filter(...)
    .with_for_update()  # Row-level lock
).scalar_one_or_none()
```

### 6. React State Mutation

```typescript
// WRONG - mutating state directly
session.sets.push(newSet)
setSession(session)

// CORRECT - immutable update
setSession({
  ...session,
  sets: [...session.sets, newSet]
})
```

### 7. 1RM Calculation Errors

```python
def calculate_1rm_epley(weight: Decimal, reps: int) -> Decimal:
    """Only valid for 1-10 reps!"""
    if reps > 10:
        raise ValueError("Epley formula not accurate for >10 reps")
    return (weight * (1 + Decimal(reps) / 30)).quantize(Decimal('0.01'))
```

### 8. SQL Injection

```python
# NEVER use string formatting
# WRONG: f"SELECT * FROM users WHERE username = '{username}'"

# CORRECT: Use ORM
db.query(User).filter(User.username == username).first()
```

### 9. XSS in User Content

```typescript
// WRONG - XSS vulnerability
<div dangerouslySetInnerHTML={{ __html: notes }} />

// CORRECT - sanitize
import DOMPurify from 'dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(notes) }} />
```

---

## Testing Strategy

### Backend Testing (pytest)

**Test Structure:**
```
backend/tests/
├── conftest.py       # Shared fixtures
├── factories.py      # Test data factories
├── unit/             # Unit tests
├── integration/      # API endpoint tests
└── e2e/              # End-to-end flows
```

**Fixtures:**
```python
# conftest.py
@pytest.fixture(scope="function")
def db_session():
    """Fresh database for each test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
```

**Factories:**
```python
# tests/factories.py
class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User

    email = Faker('email')
    username = Sequence(lambda n: f'user{n}')
    password_hash = LazyAttribute(lambda obj: hash_password('password123'))
```

**Integration Tests:**
```python
def test_create_session_success(client, auth_headers):
    payload = {"name": "Push Day", "session_date": str(date.today())}
    response = client.post("/api/sessions", json=payload, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Push Day"
```

**Coverage Requirements:**
- Minimum 80% coverage for backend
- Run: `pytest --cov=backend --cov-report=html`

### Frontend Testing

**Component Tests:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react'

it('validates required fields', async () => {
  render(<SetForm onSubmit={vi.fn()} />)

  fireEvent.click(screen.getByRole('button', { name: /submit/i }))

  expect(screen.getByText(/weight is required/i)).toBeInTheDocument()
})
```

**Hook Tests:**
```typescript
import { renderHook, waitFor } from '@testing-library/react'

it('fetches session data', async () => {
  const { result } = renderHook(() => useSession(1))

  await waitFor(() => expect(result.current.isSuccess).toBe(true))
  expect(result.current.data.id).toBe(1)
})
```

---

## Developer Experience

### Naming Conventions

**Python (Backend):**
```python
# Variables and functions: snake_case
user_id = 123
def calculate_one_rm(weight, reps): ...

# Classes: PascalCase
class WorkoutSession: ...

# Constants: UPPER_SNAKE_CASE
MAX_WEIGHT_KG = 1000
```

**TypeScript (Frontend):**
```typescript
// Variables and functions: camelCase
const userId = 123
const calculateOneRM = (weight, reps) => {...}

// Components, types: PascalCase
const WorkoutSession: React.FC = () => {...}
interface SessionData {...}

// Constants: UPPER_SNAKE_CASE
const MAX_WEIGHT_KG = 1000

// Booleans: is/has/should prefix
const isLoading = true
const hasCompleted = false
```

### Error Handling Patterns

**Backend:**
```python
# Custom exceptions
class AppException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

class NotFoundError(AppException):
    def __init__(self, resource: str, id: int):
        super().__init__(f"{resource} {id} not found", 'NOT_FOUND', 404)

# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}}
    )
```

### Logging Strategy

```python
import logging
logger = logging.getLogger(__name__)

class SessionService:
    def create_session(self, user_id, data):
        logger.info(f"Creating session for user {user_id}")
        try:
            session = self.repo.create(user_id, data)
            logger.info(f"Session {session.id} created")
            return session
        except Exception as e:
            logger.error(f"Failed to create session: {e}", exc_info=True)
            raise

# Never log: passwords, tokens, PII
```

### Environment Variables

**Backend (.env.example):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/trainer_db
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
FRONTEND_URL=http://localhost:5173
REDIS_URL=redis://localhost:6379/0
DEBUG=true
```

**Frontend (.env.example):**
```bash
VITE_API_URL=http://localhost:8000/api
VITE_ENVIRONMENT=development
```

### Git Workflow

**Branch Naming:**
```bash
feature/user-authentication
fix/login-validation
refactor/session-service
docs/api-endpoints
```

**Commit Messages:**
```bash
feat(auth): implement JWT token refresh
fix(sessions): prevent negative weight values
refactor(api): standardize error response format
docs(readme): add setup instructions
test(sessions): add integration tests
```

---

## Fitness Domain-Specific Logic

### Personal Records Detection

PRs should be automatically detected when:
- A new `Set` is logged with higher weight than previous records
- Use the `services/` layer to encapsulate PR detection logic
- Update old PRs: `is_current = False`, set `superseded_at`
- Create notification for user when new PR achieved

### Volume Calculation

```python
# Total volume = weight × reps (summed across all sets)
total_volume = sum(set.weight * set.reps for set in session.sets)
```

### 1RM Estimation Formulas

```python
# Epley: weight × (1 + reps/30)
# Brzycki: weight × 36/(37-reps)
# Only accurate for 1-10 reps!

def calculate_1rm(weight: Decimal, reps: int) -> Decimal:
    if reps > 10:
        return weight  # Conservative estimate
    return (weight * (1 + Decimal(reps) / 30)).quantize(Decimal('0.01'))
```

---

## Environment Configuration

### CORS Configuration

Backend must enable CORS for frontend origin:
- Development: `http://localhost:5173` (Vite) or `http://localhost:3000`
- Production: Specific production domain only

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## Deployment Considerations

- Backend requires WSGI/ASGI server (gunicorn/uvicorn) in production
- Database migrations must run before deployment
- Environment variables configured on hosting platform
- Frontend build artifacts served from CDN or static hosting
- Enable SSL/HTTPS on both frontend and backend
- Set up database backups and monitoring
- Configure error tracking (Sentry)
- Set up uptime monitoring

---

## Reference: todo.md

The `todo.md` file contains the complete development roadmap with ~180 tasks across 9 phases. Refer to it for:
- Detailed task breakdowns
- Feature specifications
- Recommended technology choices
- Future enhancement ideas

**Last Updated:** 2025-11-22
