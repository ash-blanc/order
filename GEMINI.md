# GEMINI.md - Order Project Context

## Project Overview
**Order** is an "Agentic Life Order System" designed to bring structure to a user's scattered digital commitments. It gathers tasks and promises from Discord, GitHub, X (Twitter), and Gmail using AI-powered agents and surfaces them through six distinct interaction modes.

### Core Technologies
- **Backend:** Python 3.13+, FastAPI, SQLAlchemy (with `aiosqlite`), Pydantic, LiteLLM.
- **Frontend:** Next.js (App Router), Tailwind CSS, TypeScript, Bun.
- **Agents:** TinyFish (for browser-based gathering), GitHub API.
- **Data Store:** SQLite (located at `~/.order/order.db` by default).

## Project Structure
- `src/order/`: Core backend logic.
    - `core/`: Database models, configuration, and SQLite storage implementation.
    - `gatherers/`: Platform-specific logic for extracting commitments (Discord, GitHub, X, Gmail).
    - `modes/`: The six functional modes of the system (One-Thing, Gather, Reduce, Conversation, Just-In-Time, Executor).
    - `synthesis/`: AI/LLM logic for extracting, filtering, and prioritizing tasks.
    - `cron/`: Background job scheduler for periodic gathering and maintenance.
    - `api.py`: FastAPI application and endpoint definitions.
- `frontend/`: Next.js frontend application.
- `main.py`: Entry point for the backend.

## Development Workflows

### Prerequisites
- Python 3.13+ and `uv` package manager.
- Node.js and `bun` package manager.
- API keys for OpenAI/OpenRouter and TinyFish.

### Building and Running

#### Backend
```bash
# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with required keys (ORDER_TINYFISH_API_KEY, ORDER_GITHUB_TOKEN, etc.)

# Start FastAPI server
uv run uvicorn order.api:app --reload
```

#### Frontend
```bash
cd frontend
# Install dependencies
bun install

# Start development server
bun run dev
```

### Key Commands
- **Backend Entry:** `uv run uvicorn order.api:app --reload`
- **CLI Entry:** `uv run order` (mapped to `order.__main__:main`)
- **Frontend Entry:** `bun run dev`

## Coding Conventions
- **Models:** Use Pydantic for data validation and SQLAlchemy for persistence. All models are defined in `src/order/core/models.py`.
- **API:** FastAPI endpoints are structured around the "modes" of the application.
- **Configuration:** Use `pydantic-settings` with an `ORDER_` prefix for environment variables (defined in `src/order/core/config.py`).
- **Async:** The backend is fully asynchronous, using `httpx` for requests and `aiosqlite` for database operations.

## Key Modes
1.  **One-Thing:** Focus on exactly one high-priority commitment.
2.  **Gather:** Pull new data from external sources.
3.  **Reduce:** AI-driven filtering and prioritization of accumulated tasks.
4.  **Conversation:** A thinking partner chat interface.
5.  **Just-In-Time:** On-demand search and retrieval of promises.
6.  **Executor:** Agent-assisted task execution.
