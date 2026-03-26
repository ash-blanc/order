# Order

**Agentic Life Order System** — Bring order to chaotic life, not another productivity tool.

## The Problem

Your work is scattered across:
- Discord chats/groups/servers
- GitHub issues/PRs
- X DMs and bookmarks
- Gmail

You don't need a better Notion. You need something that **finds what you already said you'd do**.

## The Solution

**Order** uses TinyFish web agents to gather your scattered commitments, then AI to filter, prioritize, and surface what matters.

## 6 Modes

| Mode | When | What |
|------|------|------|
| **One-Thing** | Drowning | Show only ONE commitment |
| **Gather** | Scattered | Pull from Discord, GitHub, X, Gmail |
| **Reduce** | Accumulated | Filter noise, keep what matters |
| **Conversation** | Stuck | Thinking partner chat |
| **Just-in-Time** | Specific need | Ask and receive, no storage |
| **Executor** | Ready to act | Agents handle tasks |

## Quick Start

```bash
# Setup backend
cd order
uv sync
cp .env.example .env
# Edit .env with your API keys

# Run backend
uv run uvicorn order.api:app --reload

# Setup frontend (separate terminal)
cd frontend
bun install
bun run dev
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ORDER_TINYFISH_API_KEY` | TinyFish API key (for Discord, X, Gmail) |
| `ORDER_GITHUB_TOKEN` | GitHub Personal Access Token |
| `ORDER_LLM_MODEL` | Model to use (default: openrouter/nova-pro) |
| `ORDER_OPENAI_API_KEY` | OpenAI API key |
| `ORDER_OPENROUTER_API_KEY` | OpenRouter API key |

## Architecture

```
order/
├── src/order/
│   ├── core/          # Models, config, SQLite store
│   │   ├── config.py  # Settings (API keys, env)
│   │   ├── models.py  # Commitment, Source, Priority
│   │   └── store.py   # SQLite async storage
│   │
│   ├── gatherers/     # TinyFish-based gatherers
│   │   ├── discord.py # Discord via TinyFish
│   │   ├── github.py  # GitHub API
│   │   ├── x_twitter.py # X via TinyFish
│   │   └── gmail.py   # Gmail via TinyFish
│   │
│   ├── synthesis/     # AI synthesis
│   │   └── llm.py     # Extract, filter, prioritize
│   │
│   ├── cron/          # Background jobs (OpenClaw style)
│   │   ├── scheduler.py # Hermes-style file-based cron
│   │   └── jobs.py    # Gather, reduce, expire jobs
│   │
│   ├── modes/         # 6 modes
│   │   ├── one_thing.py
│   │   ├── gather.py
│   │   ├── reduce.py
│   │   ├── conversation.py
│   │   ├── just_in_time.py
│   │   └── executor.py
│   │
│   └── api.py         # FastAPI endpoints
│
└── frontend/          # Next.js
    ├── app/
    ├── components/
    └── lib/
```

## API Endpoints

### One-Thing Mode
- `GET /api/one-thing` — Get the ONE thing to focus on
- `POST /api/one-thing/done` — Mark as done
- `POST /api/one-thing/skip` — Skip
- `GET /api/one-thing/why` — Explain why this was chosen

### Gather Mode
- `GET /api/gather` — Gather from all sources
- `GET /api/gather/test` — Test connections

### Reduce Mode
- `GET /api/reduce` — Filter and prioritize
- `GET /api/stats` — Get statistics

### Conversation Mode
- `POST /api/chat` — Chat with thinking partner
- `POST /api/chat/reset` — Reset conversation

### Just-in-Time Mode
- `POST /api/search` — Search commitments
- `GET /api/promises` — What did I promise?
- `GET /api/about?topic=X` — What about X?

### Executor Mode
- `GET /api/commitments` — List all
- `GET /api/commitments/{id}` — Get specific
- `POST /api/commitments/{id}/action` — Propose action
- `POST /api/commitments/{id}/execute` — Execute action

## Cron Jobs

The system runs background jobs automatically:
- **Gather**: Every 5 minutes
- **Reduce**: Every 10 minutes
- **Expire**: Every hour (commits older than 72h)

## Key Differentiators

1. **Not another Notion** — Pulls from where work actually lives
2. **Zero setup** — Connect accounts, done. No methodology to learn.
3. **Multiple paths to order** — 6 modes for different chaos states
4. **Always fresh** — Cron jobs keep it updated
5. **Radical simplicity** — One-Thing mode shows only ONE commitment
6. **Agentic executor** — Agents can handle tasks, not just track them

## TinyFish Integration

TinyFish provides authenticated browser automation for:
- **Discord**: No API for message search, TinyFish scrapes
- **X DMs/Bookmarks**: No API, TinyFish scrapes
- **Gmail**: Can use Gmail API or TinyFish

## License

MIT
