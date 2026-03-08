# PRP: Sift

> Implementation blueprint for parallel agent execution

---

## METADATA

| Field | Value |
|-------|-------|
| **Product** | Sift |
| **Type** | Consumer SaaS |
| **Version** | 1.0 |
| **Created** | 2026-03-07 |
| **Complexity** | High |

---

## PRODUCT OVERVIEW

**Description:** Sift is an AI-powered executive function assistant for adults with ADHD. It silently aggregates tasks from Gmail, Slack, and Notion, ranks them using a dynamic priority formula based on the user's current energy level, and surfaces exactly ONE task at a time — eliminating choice paralysis, shame spirals, and cognitive overload.

**Value Proposition:** The only productivity tool designed around executive function — not willpower. ADHD users get a shame-free, one-task-at-a-time experience that adapts to their energy state in real time.

**Complete Feature Scope:**
- [x] User registration and login (email/password)
- [x] Google OAuth login
- [x] Gmail integration (pull unresolved emails)
- [x] Slack integration (pull unresolved messages)
- [x] Notion integration (pull unresolved pages/tasks)
- [x] Manual task entry
- [x] LLM entity extraction (Google Gemini) on task import
- [x] Bandwidth Sensor (energy level slider 1-5)
- [x] Executive Function Agent (priority ranking: Score = Impact × Urgency / Energy)
- [x] Single-Card Interface (one task at a time)
- [x] Task breakdown (LLM generates 3 sub-steps)
- [x] Fresh Start Protocol (shame-free reset after absence)
- [x] Analytics Dashboard (energy trends, completion rates)
- [x] Admin Panel
- [x] Background sync worker (every 30 minutes)

---

## DESIGN LANGUAGE (STRICT)

| Token | Hex | Usage |
|-------|-----|-------|
| Deep Slate | `#0F172A` | All page backgrounds |
| Cloud Gray | `#CBD5E1` | Task cards, secondary surfaces |
| Soft Mint | `#4ECCA3` | Primary CTAs, slider, success |
| Muted Amber | `#F59E0B` | Big Rock tasks, Break Down button |
| Off White | `#F8FAFC` | Primary text on dark backgrounds |
| Muted Text | `#94A3B8` | Secondary/helper text |

- Typography: Inter or Geist
- Motion: Framer Motion (card transitions, slider glow, fade-ins only)
- Never use red in task flow — use Muted Amber for friction/warning states

---

## TECH STACK

| Layer | Technology | Skill Reference |
|-------|------------|-----------------|
| Backend | FastAPI + Python 3.11+ | skills/BACKEND.md |
| Frontend | React + TypeScript + Vite | skills/FRONTEND.md |
| Database | PostgreSQL + SQLAlchemy (async) | skills/DATABASE.md |
| Auth | JWT + bcrypt + Google OAuth | skills/BACKEND.md |
| UI | Tailwind CSS + shadcn/ui + Framer Motion | skills/FRONTEND.md |
| AI / LLM | Google Gemini (google-generativeai SDK) | — |
| Background Jobs | APScheduler | — |
| Testing | pytest + React Testing Library | skills/TESTING.md |
| Deployment | Docker + docker-compose | skills/DEPLOYMENT.md |

---

## DATABASE MODELS

### User
```
id, email, hashed_password, full_name, avatar_url,
is_active, is_verified, is_admin,
oauth_provider, oauth_id,
created_at, last_login_at
```

### RefreshToken
```
id, user_id (FK→User), token, expires_at, revoked, created_at
```

### Integration
```
id, user_id (FK→User),
provider (gmail|slack|notion),
access_token (encrypted), refresh_token (encrypted), token_expires_at,
is_active, last_synced_at,
metadata (JSON), created_at
```
Unique constraint: (user_id, provider)

### SyncLog
```
id, integration_id (FK→Integration),
synced_at, items_imported, items_updated,
status (success|error), error_message
```

### Task
```
id, user_id (FK→User), title, description,
source (gmail|slack|notion|manual), source_id,
impact (1-5), urgency (1-5), energy_required (1-5),
priority_score (float, computed),
status (active|completed|archived|snoozed),
is_big_rock (bool), sub_steps (JSON[]),
snooze_until, completed_at, archived_at,
created_at, updated_at
```
Unique constraint: (user_id, source, source_id) where source != 'manual'

### TaskMetadata
```
id, task_id (FK→Task, unique),
raw_content (text),
extracted_entities (JSON),
llm_model_used, extraction_timestamp
```

### EnergyLog
```
id, user_id (FK→User), level (1-5), logged_at, session_id
```

### FreshStartLog
```
id, user_id (FK→User),
triggered_at, tasks_archived_count, next_action_task_id
```

### DailyStats
```
id, user_id (FK→User), date (unique per user),
avg_energy_level, tasks_completed, tasks_archived,
big_rocks_completed, easy_wins_completed,
fresh_starts_triggered
```
Unique constraint: (user_id, date)

---

## MODULES

### Module 1: Authentication
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/register | Create account | Public |
| POST | /api/v1/auth/login | Login, return tokens | Public |
| POST | /api/v1/auth/refresh | Refresh access token | Public |
| POST | /api/v1/auth/logout | Revoke refresh token | Required |
| GET | /api/v1/auth/me | Get current user | Required |
| PUT | /api/v1/auth/me | Update profile | Required |
| GET | /api/v1/auth/google | Initiate Google OAuth | Public |
| GET | /api/v1/auth/google/callback | Handle Google OAuth | Public |
| POST | /api/v1/auth/forgot-password | Send reset email | Public |
| POST | /api/v1/auth/reset-password | Reset with token | Public |

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /login | LoginPage | LoginForm, GoogleOAuthButton, MintCTA |
| /register | RegisterPage | RegisterForm, GoogleOAuthButton |
| /forgot-password | ForgotPasswordPage | EmailForm |
| /reset-password | ResetPasswordPage | PasswordResetForm |
| /profile | ProfilePage | ProfileForm, AvatarUpload |

---

### Module 2: Integrations (Multi-Source Ingestor)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/integrations | List connected integrations | Required |
| DELETE | /api/v1/integrations/{id} | Disconnect integration | Required |
| POST | /api/v1/integrations/sync | Trigger full sync | Required |
| POST | /api/v1/integrations/sync/{id} | Sync specific integration | Required |
| GET | /api/v1/integrations/sync-logs | Recent sync history | Required |
| GET | /api/v1/auth/gmail | Initiate Gmail OAuth | Required |
| GET | /api/v1/auth/gmail/callback | Handle Gmail OAuth | Public |
| GET | /api/v1/auth/slack | Initiate Slack OAuth | Required |
| GET | /api/v1/auth/slack/callback | Handle Slack OAuth | Public |
| GET | /api/v1/auth/notion | Initiate Notion OAuth | Required |
| GET | /api/v1/auth/notion/callback | Handle Notion OAuth | Public |

**Services:**
- `gmail_service.py` — Gmail API client, fetch unread/starred emails as tasks
- `slack_service.py` — Slack API client, fetch unresolved DMs and mentions
- `notion_service.py` — Notion API client, fetch unchecked tasks and pages
- `sync_service.py` — Orchestrates all integration syncs, deduplication logic

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /settings/integrations | IntegrationsPage | IntegrationCard (Gmail/Slack/Notion), SyncStatus, LastSyncBadge |

---

### Module 3: Task Manager (Core Data Layer)
**Agents:** BACKEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/tasks | List tasks (filter by status, source) | Required |
| POST | /api/v1/tasks | Create task manually | Required |
| GET | /api/v1/tasks/{id} | Get task detail | Required |
| PUT | /api/v1/tasks/{id} | Update task | Required |
| DELETE | /api/v1/tasks/{id} | Archive task | Required |
| POST | /api/v1/tasks/{id}/complete | Mark task done | Required |
| POST | /api/v1/tasks/{id}/snooze | Snooze task | Required |
| POST | /api/v1/tasks/{id}/archive | Archive task | Required |
| GET | /api/v1/tasks/next | Get next recommended task | Required |
| POST | /api/v1/tasks/{id}/breakdown | LLM: generate 3 sub-steps | Required |
| PUT | /api/v1/tasks/{id}/substeps | Save sub-steps | Required |

---

### Module 4: Bandwidth Sensor (Energy Level Input)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/energy | Log energy level | Required |
| GET | /api/v1/energy/today | Get today's energy logs | Required |
| GET | /api/v1/energy/history | Get 30-day energy history | Required |

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /check-in | CheckInPage | EnergySlider (vertical, Soft Mint glow, 1-5), BandwidthPrompt, MintCTA |

**EnergySlider Spec:**
- Vertical orientation, full viewport height
- Thumb: Soft Mint `#4ECCA3` with CSS glow (`box-shadow: 0 0 20px #4ECCA3`)
- Track: Deep Slate `#0F172A` with Muted Text `#94A3B8` border
- Labels: 1=Low, 3=Medium, 5=High in Off White text
- Framer Motion: animate glow intensity on thumb drag

---

### Module 5: Executive Function Agent (AI Ranking Engine)
**Agents:** BACKEND-AGENT

**Ranking Formula:**
```python
Score = (Impact × Urgency) / Energy_Required
# Tasks with energy_required > user_energy_level → Score = 0 (suppressed)
# Big Rock = energy_required >= 4 AND impact >= 4
```

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/agent/rank | Re-rank all tasks for user + energy | Required |
| POST | /api/v1/agent/extract | Entity extraction on raw text | Internal |
| POST | /api/v1/agent/breakdown/{task_id} | Generate 3 sub-steps | Required |

**Gemini Service (`gemini_service.py`):**

Entity extraction prompt → returns JSON:
```json
{
  "title": "string",
  "impact": 1-5,
  "urgency": 1-5,
  "energy_required": 1-5,
  "is_big_rock": true/false
}
```

Task breakdown prompt → returns JSON:
```json
{
  "sub_steps": ["step 1", "step 2", "step 3"]
}
```

---

### Module 6: Single-Card Interface (Focus UX)
**Agents:** FRONTEND-AGENT

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /focus | FocusPage | TaskCard, StartButton (Mint), BreakDownButton (Amber), DoneButton (Mint), SkipButton (Ghost) |

**TaskCard Spec:**
- Background: Cloud Gray `#CBD5E1`
- Border radius: `rounded-2xl`
- Padding: `p-8`
- Title: large, Off White text
- Description: Muted Text `#94A3B8`
- Big Rock indicator: Muted Amber `#F59E0B` glow border + badge
- Sub-steps: shown inline as numbered list when expanded
- Framer Motion: `AnimatePresence` + slide-in from right on task change

**Button Spec:**
- Start: `bg-[#4ECCA3] text-[#0F172A] font-bold` — becomes "Done" after click
- Break Down: `bg-[#F59E0B] text-[#0F172A]` — shows sub-steps inline
- Skip: `variant="ghost" text-[#94A3B8]` — no confirmation needed

**Flow:**
1. On mount: GET /api/v1/tasks/next?energy_level={current}
2. "Start" → mark in-progress locally, button becomes "Done"
3. "Done" → POST /tasks/{id}/complete → AnimatePresence exit → load next
4. "Break Down" → POST /agent/breakdown/{id} → show sub-steps inline
5. "Skip" → GET /tasks/next again (re-rank)

---

### Module 7: Fresh Start Protocol (Shame-Gate)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/freshstart/check | Check if trigger threshold met | Required |
| POST | /api/v1/freshstart/reset | Archive stale tasks, log reset | Required |
| GET | /api/v1/freshstart/history | Past reset log | Required |

**Trigger Logic:**
- Threshold: `last_login_at < now() - 18 hours`
- On reset: set all `active` tasks older than threshold to `archived`
- Return single recommended next action (lowest energy_required, highest score)

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /fresh-start | FreshStartPage | FreshStartCard, SingleActionCard, LetsDoThisCTA |

**FreshStartPage Spec:**
- Full-screen Deep Slate background
- Large Soft Mint icon (checkmark or leaf SVG)
- Headline: "Welcome back." (Off White, large)
- Subtext: "Everything's been cleared. What's ONE thing you can do right now?" (Muted Text)
- Single Cloud Gray task card (recommended task)
- CTA: "Let's do this" in Soft Mint → navigates to /focus
- NO red, NO "overdue", NO shame language anywhere

**App Startup Flow:**
```
App loads
  → GET /freshstart/check
  → if triggered: redirect to /fresh-start
  → else: redirect to /check-in
  → /check-in → /focus
```

---

### Module 8: Analytics Dashboard
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/analytics/summary | Last 7 days summary | Required |
| GET | /api/v1/analytics/trends | 30-day energy + completion trends | Required |
| GET | /api/v1/analytics/completion-rate | Overall completion % | Required |

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /analytics | AnalyticsPage | EnergyTrendChart, CompletionBarChart, BigRockRatio, FreshStartCounter |

**Chart Spec:**
- Library: Recharts
- All charts on Deep Slate background
- Energy trend: line chart, Soft Mint line color
- Completion: bar chart, Soft Mint bars for completed, Muted Amber for Big Rocks
- Labels: Off White, Muted Text for secondary

---

### Module 9: Admin Panel
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/admin/users | List all users + stats | Admin |
| PUT | /api/v1/admin/users/{id} | Update user status | Admin |
| GET | /api/v1/admin/stats | Platform-wide stats | Admin |
| GET | /api/v1/admin/integrations | Integration health | Admin |
| GET | /api/v1/admin/sync-logs | Recent sync activity | Admin |

**Frontend Pages:**
| Route | Page | Key Components |
|-------|------|----------------|
| /admin | AdminDashboard | StatsCards, RecentActivity |
| /admin/users | AdminUsersPage | UsersTable, StatusToggle |

---

## PHASE EXECUTION PLAN

### Phase 1: Foundation (4 agents in parallel)

**DATABASE-AGENT:**
- Read: `skills/DATABASE.md`
- Create: `backend/app/database.py` (async SQLAlchemy setup)
- Create: all model files in `backend/app/models/`
  - `user.py` (User, RefreshToken)
  - `task.py` (Task, TaskMetadata)
  - `integration.py` (Integration, SyncLog)
  - `energy.py` (EnergyLog)
  - `freshstart.py` (FreshStartLog)
  - `analytics.py` (DailyStats)
- Create: `backend/app/models/__init__.py`
- Create: `backend/alembic/` with initial migration
- Validate: `alembic upgrade head`

**BACKEND-AGENT (Foundation):**
- Read: `skills/BACKEND.md`
- Create: `backend/app/main.py` (FastAPI app, CORS, routers)
- Create: `backend/app/config.py` (Settings with pydantic-settings)
- Create: `backend/app/auth/` (JWT utilities, password hashing, OAuth helpers)
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`

**FRONTEND-AGENT (Foundation):**
- Read: `skills/FRONTEND.md`
- Initialize: Vite + React + TypeScript project
- Setup: Tailwind CSS config with Sift design tokens
- Setup: shadcn/ui components
- Create: `frontend/src/types/index.ts` (all TypeScript interfaces)
- Create: `frontend/src/services/api.ts` (Axios instance, interceptors)
- Create: `frontend/src/context/AuthContext.tsx`
- Create: base layout components (AppLayout, ProtectedRoute)
- Create: `frontend/.env.example`

**DEVOPS-AGENT:**
- Read: `skills/DEPLOYMENT.md`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml` (backend, frontend, postgres, redis)
- Create: `docker-compose.dev.yml`
- Create: `.github/workflows/ci.yml`
- Create: `.env.example` (root level)

**Validation Gate 1:**
```bash
cd backend && pip install -r requirements.txt
alembic upgrade head
cd ../frontend && npm install
docker-compose config
```

---

### Phase 2: Backend Modules (parallel)

**BACKEND-AGENT — Auth Module:**
- Create: `backend/app/routers/auth.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/auth_service.py`
- Validate: `ruff check backend/app/routers/auth.py`

**BACKEND-AGENT — Integrations + Sync:**
- Create: `backend/app/routers/integrations.py`
- Create: `backend/app/schemas/integration.py`
- Create: `backend/app/services/gmail_service.py`
- Create: `backend/app/services/slack_service.py`
- Create: `backend/app/services/notion_service.py`
- Create: `backend/app/services/sync_service.py`
- Create: `backend/app/workers/sync_worker.py` (APScheduler)

**BACKEND-AGENT — Tasks + Agent:**
- Create: `backend/app/routers/tasks.py`
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/services/task_service.py`
- Create: `backend/app/services/gemini_service.py`
- Create: `backend/app/services/ranking_service.py`
- Create: `backend/app/routers/agent.py`

**BACKEND-AGENT — Energy + FreshStart + Analytics + Admin:**
- Create: `backend/app/routers/energy.py`
- Create: `backend/app/routers/freshstart.py`
- Create: `backend/app/routers/analytics.py`
- Create: `backend/app/routers/admin.py`
- Create: corresponding schemas and services

**Validation Gate 2:**
```bash
ruff check backend/
mypy backend/app/ --ignore-missing-imports
curl http://localhost:8000/docs  # Swagger UI loads
```

---

### Phase 3: Frontend Modules (parallel)

**FRONTEND-AGENT — Auth Pages:**
- Create: `frontend/src/pages/LoginPage.tsx`
- Create: `frontend/src/pages/RegisterPage.tsx`
- Create: `frontend/src/pages/ForgotPasswordPage.tsx`
- Create: `frontend/src/pages/ResetPasswordPage.tsx`
- Create: `frontend/src/pages/ProfilePage.tsx`

**FRONTEND-AGENT — Core Experience:**
- Create: `frontend/src/pages/CheckInPage.tsx` (Bandwidth Sensor)
- Create: `frontend/src/components/EnergySlider/EnergySlider.tsx`
- Create: `frontend/src/pages/FocusPage.tsx` (Single-Card Interface)
- Create: `frontend/src/components/TaskCard/TaskCard.tsx`
- Create: `frontend/src/pages/FreshStartPage.tsx`

**FRONTEND-AGENT — Supporting Pages:**
- Create: `frontend/src/pages/Settings/IntegrationsPage.tsx`
- Create: `frontend/src/components/IntegrationCard/IntegrationCard.tsx`
- Create: `frontend/src/pages/AnalyticsPage.tsx`
- Create: `frontend/src/pages/Admin/AdminDashboard.tsx`
- Create: `frontend/src/pages/Admin/AdminUsersPage.tsx`

**FRONTEND-AGENT — Hooks + Services:**
- Create: `frontend/src/hooks/useTasks.ts`
- Create: `frontend/src/hooks/useEnergy.ts`
- Create: `frontend/src/hooks/useFreshStart.ts`
- Create: `frontend/src/services/taskService.ts`
- Create: `frontend/src/services/integrationService.ts`
- Create: `frontend/src/services/energyService.ts`

**Validation Gate 3:**
```bash
cd frontend && npm run lint
npm run type-check
npm run build
```

---

### Phase 4: Quality (3 agents in parallel)

**TEST-AGENT:**
- Read: `skills/TESTING.md`
- Create: `backend/tests/test_auth.py`
- Create: `backend/tests/test_tasks.py`
- Create: `backend/tests/test_integrations.py`
- Create: `backend/tests/test_agent.py`
- Create: `backend/tests/test_freshstart.py`
- Create: `frontend/src/__tests__/EnergySlider.test.tsx`
- Create: `frontend/src/__tests__/TaskCard.test.tsx`
- Create: `frontend/src/__tests__/FocusPage.test.tsx`
- Target: 80%+ backend coverage

**REVIEW-AGENT:**
- Audit: OAuth token encryption in Integration model
- Audit: Rate limiting on auth endpoints (slowapi)
- Audit: CSRF state parameter validation in all OAuth flows
- Audit: SQL injection safety (verify ORM usage, no raw queries)
- Audit: Gemini API error handling and fallback behavior
- Audit: TypeScript strict mode compliance
- Audit: No hardcoded secrets in any file

**DEVOPS-AGENT (Final):**
- Verify: `docker-compose up -d` succeeds
- Verify: All health checks pass
- Verify: APScheduler sync worker starts correctly
- Verify: Database migrations run on container start

**Validation Gate 4 (Final):**
```bash
pytest backend/tests/ -v --cov=app --cov-fail-under=80
cd frontend && npm test -- --coverage
docker-compose up -d
curl http://localhost:8000/health
curl http://localhost:5173
```

---

## VALIDATION GATES SUMMARY

| Gate | When | Commands |
|------|------|----------|
| 1 | After Phase 1 | `pip install -r requirements.txt`, `alembic upgrade head`, `npm install`, `docker-compose config` |
| 2 | After Phase 2 | `ruff check backend/`, `mypy backend/`, Swagger UI loads |
| 3 | After Phase 3 | `npm run lint`, `npm run type-check`, `npm run build` |
| 4 (Final) | After Phase 4 | `pytest --cov-fail-under=80`, `npm test`, `docker-compose up`, health checks |

---

## ENVIRONMENT VARIABLES

```env
# Database
DATABASE_URL=postgresql+asyncpg://sift:siftpass@localhost:5432/sift

# Auth
SECRET_KEY=change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google (Login + Gmail)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Gmail
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret

# Slack
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret

# Notion
NOTION_CLIENT_ID=your-notion-client-id
NOTION_CLIENT_SECRET=your-notion-client-secret

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key

# Token Encryption (Fernet key for OAuth tokens at rest)
ENCRYPTION_KEY=your-fernet-encryption-key

# App Config
FRESH_START_THRESHOLD_HOURS=18
SYNC_INTERVAL_MINUTES=30
FRONTEND_URL=http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## FILE OUTPUT MANIFEST

### Backend (expected files)
```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── integration.py
│   │   ├── energy.py
│   │   ├── freshstart.py
│   │   └── analytics.py
│   ├── schemas/
│   │   ├── auth.py, task.py, integration.py
│   │   ├── energy.py, freshstart.py, analytics.py
│   ├── routers/
│   │   ├── auth.py, tasks.py, integrations.py
│   │   ├── agent.py, energy.py, freshstart.py
│   │   ├── analytics.py, admin.py
│   ├── services/
│   │   ├── auth_service.py, task_service.py
│   │   ├── gmail_service.py, slack_service.py, notion_service.py
│   │   ├── sync_service.py, gemini_service.py, ranking_service.py
│   ├── auth/
│   │   ├── jwt.py, dependencies.py, oauth.py
│   └── workers/
│       └── sync_worker.py
├── alembic/
├── tests/
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Frontend (expected files)
```
frontend/
├── src/
│   ├── types/index.ts
│   ├── services/
│   │   ├── api.ts, authService.ts, taskService.ts
│   │   ├── integrationService.ts, energyService.ts
│   ├── context/AuthContext.tsx
│   ├── hooks/
│   │   ├── useAuth.ts, useTasks.ts, useEnergy.ts, useFreshStart.ts
│   ├── components/
│   │   ├── ui/ (shadcn)
│   │   ├── TaskCard/TaskCard.tsx
│   │   ├── EnergySlider/EnergySlider.tsx
│   │   ├── IntegrationCard/IntegrationCard.tsx
│   │   └── layout/ (AppLayout, ProtectedRoute)
│   ├── pages/
│   │   ├── LoginPage.tsx, RegisterPage.tsx
│   │   ├── ForgotPasswordPage.tsx, ResetPasswordPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── CheckInPage.tsx
│   │   ├── FocusPage.tsx
│   │   ├── FreshStartPage.tsx
│   │   ├── AnalyticsPage.tsx
│   │   ├── Settings/IntegrationsPage.tsx
│   │   └── Admin/ (AdminDashboard.tsx, AdminUsersPage.tsx)
│   └── App.tsx (router setup)
├── Dockerfile
└── .env.example
```

---

## AGENT DISPATCH SUMMARY

| Agent | Phase | Outputs |
|-------|-------|---------|
| DATABASE-AGENT | 1 | 6 model files, alembic migrations, database.py |
| BACKEND-AGENT | 1+2 | main.py, config.py, 8 routers, 8+ services, auth/ |
| FRONTEND-AGENT | 1+3 | Vite setup, types, context, 10+ pages, components |
| DEVOPS-AGENT | 1+4 | Docker files, docker-compose, CI workflow |
| TEST-AGENT | 4 | pytest suite (80%+), RTL tests |
| REVIEW-AGENT | 4 | Security audit report, fixes |

---

## NEXT STEP

Execute with parallel agents:

```bash
/execute-prp PRPs/sift-prp.md
```
