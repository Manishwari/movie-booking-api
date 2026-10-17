
# Movie Ticket Booking API

A RESTful backend API for a movie ticket booking system, built with FastAPI and PostgreSQL. The application supports movie management, theater and show management, user authentication, seat selection, and ticket bookings.

## Features

- **Movie Management** — Create, retrieve, update, and delete movies.
- **Theater Management** — Manage theaters and their screens.
- **Screen and Seat Management** — Organize screens and available seats.
- **Show Management** — Manage movie shows and their schedules.
- **User Authentication** — Secure authentication using JWT tokens.
- **Role-Based Authorization** — Support for Customer, Theater Owner, and Admin roles.
- **Ticket Booking** — Create bookings and retrieve booking details.
- **Booking Cancellation** — Cancel bookings through the API.
- **Seat Availability Protection** — Prevent duplicate seat bookings and handle concurrent booking attempts.
- **Database Migrations** — Manage database schema changes using Alembic.
- **Automated Testing** — Test API endpoints and business logic using pytest.
- **Code Quality** — Use Ruff and mypy for linting, formatting, and type checking.
- **Containerized Database** — Run PostgreSQL using Docker Compose.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.14 | Programming language |
| FastAPI | REST API framework |
| Pydantic | Data validation |
| SQLAlchemy 2.0 | Asynchronous ORM |
| PostgreSQL | Relational database |
| asyncpg | Async PostgreSQL driver |
| Alembic | Database migrations |
| JWT | Authentication |
| pytest | Automated testing |
| Ruff | Linting and formatting |
| mypy | Static type checking |
| Docker Compose | Database container management |
| uv | Python dependency and project management |

## Prerequisites

Install the following tools before running the project:

- Python 3.14
- uv
- Docker Desktop
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Manishwari/movie-booking-api.git
cd movie-booking-api
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create your local `.env` file using the project's `.env.example` if needed.

In PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the required database connection settings and authentication secrets in `.env`. Never commit real secrets to GitHub.

### 4. Start PostgreSQL

```bash
docker compose up -d db
```

Check the database container:

```bash
docker compose ps
```

### 5. Apply database migrations

```bash
uv run poe migrate
```

### 6. Start the API server

```bash
uv run poe dev
```

The API will be available at:

http://127.0.0.1:8000

## API Documentation

FastAPI automatically generates interactive API documentation.

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Use Swagger UI to explore endpoints, provide request data, authenticate, and test API operations.

## API Modules

The API includes endpoints for the following resources:

| Module | Functionality |
|---|---|
| Movies | Retrieve and manage movie records |
| Theaters | Manage theaters |
| Screens | Manage screens within theaters |
| Seats | Manage seats and seat information |
| Shows | Manage scheduled movie shows |
| Authentication | Register, log in, and obtain authentication tokens |
| Bookings | Create, retrieve, and cancel ticket bookings |

API routes are organized under the `/api/v1` prefix.

### Example: Retrieve movies

**Endpoint**

```http
GET /api/v1/movies?limit=50&offset=0
```

**Example response**

```json
[
  {
    "id": "2b446b44-d0ee-422a-85e6-b16c76e3bfe1",
    "name": "Pushpa 2: The Rule",
    "description": "An action drama movie about Pushpa Raj and his rise in the red sandalwood smuggling world.",
    "created_at": "2026-10-15T11:23:39.084041Z"
  }
]
```

The response above illustrates the movie resource structure; actual results depend on the database contents.

## Booking Endpoints

The booking module provides operations to create and manage customer bookings.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/bookings/` | Create a booking |
| GET | `/api/v1/bookings/` | Retrieve bookings for the authenticated customer |
| GET | `/api/v1/bookings/{id}` | Retrieve a booking by ID |
| POST | `/api/v1/bookings/{id}/cancel` | Cancel a booking |

Authentication and authorization rules apply to protected endpoints.

For the complete request and response schemas, use the Swagger documentation.

## Testing

Run the automated test suite:

```bash
uv run poe test
```

Run linting, formatting checks, and type checking:

```bash
uv run poe lint
```

Format and automatically fix supported code issues:

```bash
uv run poe fmt
```

The project has previously passed **21 tests**, and Ruff and mypy checks passed. Run the commands again after making changes to verify the current state.

## Database Migrations

Apply pending migrations:

```bash
uv run poe migrate
```

Generate a migration:

```bash
uv run poe revision -m "describe the change"
```

Review generated migration files before applying them.

## Project Structure

```text
movie-booking-api/
├── src/
│   └── movie_booking_api/
│       ├── main.py
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── auth/
│       ├── movies/
│       ├── theaters/
│       ├── screens/
│       ├── seats/
│       ├── shows/
│       └── bookings/
├── alembic/
├── tests/
├── docs/
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

The directory names above illustrate the intended organization. Refer to the actual repository for the exact current file and directory names.

## Security

- Keep database credentials and authentication secrets in environment variables.
- Do not commit `.env` or other files containing secrets.
- Use authentication and role-based authorization for protected operations.
- Validate incoming requests and handle booking conflicts safely.

## Future Improvements

- Payment gateway integration
- Email or SMS booking confirmations
- Production deployment and monitoring

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
