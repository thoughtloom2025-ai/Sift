# CLAUDE.md - Sift Project Rules

> Project-specific rules for Claude Code. This file is read automatically.

---

## Project Overview

**Product:** Sift
**Description:** AI-powered executive function assistant for ADHD users. Aggregates tasks from Gmail, Slack, and Notion, then surfaces ONE task at a time based on the user's current energy level.
**Tech Stack:**
- Backend: FastAPI + Python 3.11+
- Frontend: React + Vite + TypeScript
- Database: PostgreSQL + SQLAlchemy (async)
- Auth: JWT + Google OAuth
- UI: Tailwind CSS + shadcn/ui + Framer Motion
- AI: Google Gemini

---

## Design Language (STRICT — Never Deviate)

| Token | Hex | Usage |
|-------|-----|-------|
| Deep Slate | `#0F172A` | All page backgrounds |
| Cloud Gray | `#CBD5E1` | Task cards, secondary surfaces |
| Soft Mint | `#4ECCA3` | Primary CTAs, slider, success states |
| Muted Amber | `#F59E0B` | Big Rock tasks, Break Down button |
| Off White | `#F8FAFC` | Primary text on dark backgrounds |
| Muted Text | `#94A3B8` | Secondary/helper text |

- Typography: Inter or Geist only
- Motion: Framer Motion for card transitions, slider glow, fade-ins
- Never use red for overdue/error states in the task flow — use Muted Amber or neutral
- Never show task lists — only single-card views

---

## Project Structure

```
sift/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── integration.py
│   │   │   ├── energy.py
│   │   │   ├── freshstart.py
│   │   │   └── analytics.py
│   │   ├── schemas/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   ├── integrations.py
│   │   │   ├── energy.py
│   │   │   ├── agent.py
│   │   │   ├── freshstart.py
│   │   │   ├── analytics.py
│   │   │   └── admin.py
│   │   ├── services/
│   │   │   ├── gmail_service.py
│   │   │   ├── slack_service.py
│   │   │   ├── notion_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── ranking_service.py
│   │   │   └── sync_service.py
│   │   └── auth/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          # shadcn/ui components
│   │   │   ├── TaskCard/
│   │   │   ├── EnergySlider/
│   │   │   └── FreshStart/
│   │   ├── pages/
│   │   │   ├── CheckIn.tsx      # Bandwidth Sensor
│   │   │   ├── Focus.tsx        # Single-Card Interface
│   │   │   ├── FreshStart.tsx   # Fresh Start Protocol
│   │   │   ├── Analytics.tsx
│   │   │   ├── Settings/
│   │   │   │   └── Integrations.tsx
│   │   │   └── Admin/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── context/
│   │   └── types/
│   └── package.json
├── skills/
├── agents/
├── PRPs/
└── .claude/commands/
```

---

## Code Standards

### Python (Backend)
```python
# ALWAYS use type hints
async def get_next_task(
    db: AsyncSession,
    user_id: int,
    energy_level: int
) -> Task | None:
    pass

# ALWAYS async endpoints
@router.get("/tasks/next")
async def get_next_task(
    energy_level: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    pass
```

### TypeScript (Frontend)
```typescript
// ALWAYS define interfaces
interface Task {
  id: number;
  title: string;
  description: string;
  source: 'gmail' | 'slack' | 'notion' | 'manual';
  impact: number;
  urgency: number;
  energyRequired: number;
  priorityScore: number;
  isBigRock: boolean;
  subSteps: string[];
  status: 'active' | 'completed' | 'archived' | 'snoozed';
}

// NO any types
const fetchNextTask = async (energyLevel: number): Promise<Task> => { ... };
```

---

## Module-Specific Rules

### Task Ranking
- Priority score formula: `Score = (Impact × Urgency) / Energy Required`
- Tasks with `energy_required > user_energy_level` MUST be suppressed (score = 0)
- Big Rocks = `energy_required >= 4` AND `impact >= 4`
- Never show more than one task at a time in the Focus UI

### Integrations
- OAuth tokens MUST be encrypted at rest (use Fernet or similar)
- Never log raw OAuth tokens
- Sync jobs run every 30 minutes via APScheduler
- Duplicate detection: use `source` + `source_id` as unique constraint
- Failed syncs must be logged to SyncLog with full error details

### Fresh Start Protocol
- Absence threshold: 18 hours since last_login_at
- Check on every app load via GET /freshstart/check
- Archived tasks are NEVER deleted — only status changed to 'archived'
- Fresh Start redirect MUST happen before /check-in

### LLM (Google Gemini)
- Use `google-generativeai` Python SDK
- Entity extraction must return: title, impact (1-5), urgency (1-5), energy_required (1-5), is_big_rock
- Task breakdown must return exactly 3 sub-steps as a JSON array
- Always handle Gemini API errors gracefully — fall back to manual defaults

### Design (Strict)
- Background: ALWAYS `#0F172A` (Deep Slate)
- Primary action buttons: ALWAYS `#4ECCA3` (Soft Mint)
- Big Rock indicator: ALWAYS `#F59E0B` (Muted Amber)
- Never use red in the task flow
- Task cards: ALWAYS `#CBD5E1` (Cloud Gray)

---

## Forbidden Patterns

### Backend
- Never use `print()` — use `logging`
- Never store passwords in plain text — use bcrypt
- Never hardcode secrets — use environment variables
- Never use synchronous SQLAlchemy when async is configured
- Never skip input validation — use Pydantic everywhere
- Never log OAuth tokens or user credentials

### Frontend
- Never use `any` type in TypeScript
- Never leave `console.log` in production code
- Never use inline styles — use Tailwind classes
- Never show a task list — only single-card interface
- Never use red color for overdue states

---

## API Conventions

- All endpoints prefixed with `/api/v1/`
- Use plural nouns: `/tasks`, `/integrations`, `/energy`
- HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request (validation)
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Not Found
  - 409: Conflict (duplicate)
  - 422: Unprocessable Entity (Pydantic)

---

## Authentication

### JWT Configuration
- Access token expires: 30 minutes
- Refresh token expires: 7 days
- Algorithm: HS256

### OAuth Providers
- Google OAuth 2.0: login + profile
- Gmail OAuth: email ingestion (read-only)
- Slack OAuth: message ingestion
- Notion OAuth: page/task ingestion
- Always verify state parameter for CSRF protection on all OAuth flows

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sift

# Auth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google (Login + Gmail)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Slack
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret

# Notion
NOTION_CLIENT_ID=your-notion-client-id
NOTION_CLIENT_SECRET=your-notion-client-secret

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Token encryption
ENCRYPTION_KEY=your-fernet-key

# Frontend
VITE_API_URL=http://localhost:8000

# App
FRESH_START_THRESHOLD_HOURS=18
SYNC_INTERVAL_MINUTES=30
```

---

## Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker-compose up -d

# Tests
pytest backend/tests -v --cov=app
cd frontend && npm test

# Linting
ruff check backend/
cd frontend && npm run lint && npm run type-check
```

---

## Skills Reference

| Task | Skill |
|------|-------|
| Database models | skills/DATABASE.md |
| API + Auth | skills/BACKEND.md |
| React + UI | skills/FRONTEND.md |
| Testing | skills/TESTING.md |
| Deployment | skills/DEPLOYMENT.md |

---

## Agent Coordination

| Agent | Role |
|-------|------|
| DATABASE-AGENT | Models + migrations (User, Task, Integration, EnergyLog, FreshStartLog, DailyStats) |
| BACKEND-AGENT | API endpoints + services + Gemini integration |
| FRONTEND-AGENT | UI pages + components (Focus, CheckIn, FreshStart, Analytics) |
| DEVOPS-AGENT | Docker + background jobs + CI/CD |
| TEST-AGENT | Unit + integration tests |
| REVIEW-AGENT | Security + code quality audit |

---

## Validation

```bash
ruff check backend/ && pytest
npm run lint && npm run type-check
docker-compose build
```
