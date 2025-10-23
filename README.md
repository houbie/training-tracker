# Training Tracker

A full-stack application for tracking training sessions with date, duration, and distance.

## Features

### Backend (FastAPI)
- Create, read, update, and delete training sessions
- Filter sessions by date range
- Get aggregated statistics (total/average duration, distance, pace)
- Pagination support
- OpenAPI/Swagger documentation
- Full test coverage

### Frontend (React)
- Modern, responsive UI with dark theme
- Create and edit training sessions
- View all sessions in a table
- Real-time statistics dashboard
- Delete sessions with confirmation

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **pytest** - Testing
- **mypy** - Type checking
- **ruff** - Linting and formatting
- **uv** - Fast package management

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## Quick Start

### Backend

```bash
# Install dependencies
./pw install-dev

# Run the API server
./pw run
```

The API will be available at `http://localhost:8080`
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Frontend

```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Run development server
npm run dev
```

The UI will be available at `http://localhost:3000`

## Project Structure

```
training-tracker/
├── src/training_tracker/      # Python backend
│   ├── main.py                # FastAPI app
│   ├── routes.py              # API endpoints
│   ├── models.py              # Pydantic models
│   └── storage.py             # Data storage
├── tests/                     # Backend tests
│   └── test_api.py           # API tests
├── ui/                        # React frontend
│   └── src/
│       ├── components/        # React components
│       ├── App.tsx           # Main app
│       ├── api.ts            # API client
│       └── types.ts          # TypeScript types
├── pyproject.toml            # Python config
└── openapi.yaml              # API specification
```

## API Endpoints

### Training Sessions
- `GET /v1/training-sessions` - List all training sessions
  - Query params: `startDate`, `endDate`, `limit`, `offset`
- `POST /v1/training-sessions` - Create a new training session
- `GET /v1/training-sessions/{id}` - Get a specific training session
- `PUT /v1/training-sessions/{id}` - Update a training session
- `DELETE /v1/training-sessions/{id}` - Delete a training session
- `GET /v1/training-sessions/statistics` - Get training statistics
  - Query params: `startDate`, `endDate`

## Development

### Backend

```bash
# Run tests
./pw test

# Format code
./pw format

# Lint code
./pw lint

# Type check
./pw check-mypy
```

### Frontend

```bash
cd ui

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Data Model

### TrainingSession

- `id` (string, UUID) - Unique identifier
- `date` (date) - Date of the training session (YYYY-MM-DD)
- `duration` (float) - Duration in minutes
- `distance` (float) - Distance in kilometers
- `notes` (string, optional) - Additional notes
- `createdAt` (datetime) - Creation timestamp
- `updatedAt` (datetime) - Last update timestamp

## Example Usage

### Create a training session

```bash
curl -X POST "http://localhost:8080/v1/training-sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-10-23",
    "duration": 45.5,
    "distance": 8.5,
    "notes": "Morning run with intervals"
  }'
```

### Get statistics

```bash
curl "http://localhost:8080/v1/training-sessions/statistics"
```

## Storage

Currently uses in-memory storage with example data loaded on startup. For production, integrate with a database like PostgreSQL, MongoDB, or SQLite.

## License

MIT
