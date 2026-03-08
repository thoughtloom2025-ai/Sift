# INITIAL.md - Sift Product Definition

> An AI-powered executive function assistant that connects to Slack, Gmail, and Notion, ingests all "unresolved" items, and surfaces exactly ONE task at a time based on the user's current energy level using a dynamic priority ranking formula — designed specifically for users with ADHD.

---

## PRODUCT

### Name
Sift

### Description
Sift is a focus-first productivity app built for ADHD brains. It silently aggregates tasks from Gmail, Slack, and Notion, then uses an AI ranking agent to surface the single best task for the user's current energy state — eliminating choice paralysis, shame spirals, and cognitive overload.

### Target User
Adults with ADHD (and executive function challenges) who struggle with task prioritization, decision fatigue, and the emotional weight of overdue to-do lists.

### Type
- [x] Consumer SaaS

---

## TECH STACK

| Layer | Choice |
|-------|--------|
| Backend | FastAPI + Python 3.11+ |
| Frontend | React + Vite + TypeScript |
| Database | PostgreSQL + SQLAlchemy (async) |
| Auth | JWT + Google OAuth |
| UI | Tailwind CSS + shadcn/ui + Framer Motion |
| AI / LLM | Google Gemini |
| Background Jobs | APScheduler |
| Payments | None |

---

## DESIGN LANGUAGE

Sift has a precise, intentional visual identity. All UI must adhere to these colors:

| Token | Hex | Usage |
|-------|-----|-------|
| Deep Slate | `#0F172A` | Page backgrounds |
| Cloud Gray | `#CBD5E1` | Task cards, secondary surfaces |
| Soft Mint | `#4ECCA3` | Primary actions (Start button, slider, CTAs) |
| Muted Amber | `#F59E0B` | Complex tasks (Big Rocks), Break Down button |
| Off White | `#F8FAFC` | Primary text on dark backgrounds |
| Muted Text | `#94A3B8` | Secondary/helper text |

Typography: Inter or Geist. Clean, minimal, no decorative fonts.
Motion: Subtle Framer Motion animations — card transitions, slider glow, fade-ins only.

---

## MODULES

### Module 1: Authentication (Required)

**Description:** User authentication, authorization, and profile management.

**Models:**
```
User:
  - id, email, hashed_password, full_name, avatar_url
  - is_active, is_verified, oauth_provider, oauth_id
  - created_at, last_login_at

RefreshToken:
  - id, user_id (FK), token, expires_at, revoked, created_at
```

**Endpoints:**
```
POST /auth/register           - Create new account
POST /auth/login              - Login, return tokens
POST /auth/refresh            - Exchange refresh token
POST /auth/logout             - Revoke refresh token
GET  /auth/me                 - Get current user profile
PUT  /auth/me                 - Update profile
GET  /auth/google             - Initiate Google OAuth
GET  /auth/google/callback    - Handle Google OAuth callback
POST /auth/forgot-password    - Send reset email
POST /auth/reset-password     - Reset with token
```

**Pages:**
```
/login            - Login (email/password + Google button)
/register         - Registration
/forgot-password  - Forgot password flow
/reset-password   - Reset password with token
/profile          - User profile settings (protected)
```

---

### Module 2: Integrations (Multi-Source Ingestor)

**Description:** Connect Sift to Gmail, Slack, and Notion. Pull "unresolved" items silently into the background database. Users never see a cluttered import list — items flow invisibly into the task engine.

**Models:**
```
Integration:
  - id, user_id (FK), provider (gmail|slack|notion)
  - access_token (encrypted), refresh_token (encrypted)
  - token_expires_at, is_active, last_synced_at
  - metadata (JSON), created_at

SyncLog:
  - id, integration_id (FK), synced_at
  - items_imported, items_updated, status, error_message
```

**Endpoints:**
```
GET    /integrations              - List user's connected integrations
DELETE /integrations/{id}         - Disconnect an integration
POST   /integrations/sync         - Manually trigger full sync
POST   /integrations/sync/{id}    - Sync a specific integration
GET    /integrations/sync-logs    - Recent sync history

GET    /auth/gmail                - Initiate Gmail OAuth
GET    /auth/gmail/callback       - Handle Gmail OAuth
GET    /auth/slack                - Initiate Slack OAuth
GET    /auth/slack/callback       - Handle Slack OAuth
GET    /auth/notion               - Initiate Notion OAuth
GET    /auth/notion/callback      - Handle Notion OAuth
```

**Pages:**
```
/settings/integrations  - Connect/disconnect Gmail, Slack, Notion
                          with status indicators and last-synced timestamps
```

**Background Jobs:**
- Periodic sync worker (APScheduler) runs every 30 minutes per active integration

---

### Module 3: Task Manager (Core Data Layer)

**Description:** The central task repository. All tasks — whether ingested from integrations or entered manually — live here. Each task has LLM-extracted metadata for the ranking agent.

**Models:**
```
Task:
  - id, user_id (FK), title, description
  - source (gmail|slack|notion|manual), source_id
  - impact (1-5), urgency (1-5), energy_required (1-5)
  - priority_score (float, computed)
  - status (active|completed|archived|snoozed)
  - is_big_rock (bool), sub_steps (JSON array)
  - snooze_until, completed_at, archived_at
  - created_at, updated_at

TaskMetadata:
  - id, task_id (FK), raw_content
  - extracted_entities (JSON), llm_model_used
  - extraction_timestamp
```

**Endpoints:**
```
GET    /tasks              - List tasks (filtered by status, source)
POST   /tasks              - Create task manually
GET    /tasks/{id}         - Get task detail
PUT    /tasks/{id}         - Update task
DELETE /tasks/{id}         - Archive a task
POST   /tasks/{id}/complete  - Mark task as done
POST   /tasks/{id}/snooze    - Snooze task until later
POST   /tasks/{id}/archive   - Archive task
GET    /tasks/next           - Get next recommended task (calls ranking agent)
POST   /tasks/{id}/breakdown - LLM: break task into 3 sub-steps
PUT    /tasks/{id}/substeps  - Save sub-steps
```

---

### Module 4: Bandwidth Sensor (Energy Level Input)

**Description:** The entry screen. A minimalist view with a large, glowing Soft Mint vertical slider that captures the user's Executive Function level (1-5) for the session. This value gates which tasks are surfaced.

**Models:**
```
EnergyLog:
  - id, user_id (FK), level (1-5), logged_at, session_id
```

**Endpoints:**
```
POST /energy          - Log energy level for current session
GET  /energy/today    - Get today's energy log(s)
GET  /energy/history  - Energy history (last 30 days, for analytics)
```

**Pages:**
```
/check-in  - The Bandwidth Sensor entry screen:
             - Deep Slate background
             - Large glowing vertical Soft Mint slider (1-5)
             - Prompt: "How's your bandwidth right now?"
             - CTA: "Show me what I can do" → /focus
             - Framer Motion glow effect on slider thumb
```

---

### Module 5: Executive Function Agent (AI Ranking Engine)

**Description:** The brain of Sift. A service layer that ranks all active tasks using:
`Score = (Impact × Urgency) / Energy Required`

The user's current energy level acts as a Gatekeeper — tasks with energy_required > user_level are suppressed. Big Rocks (high energy) are only shown to users at level 4-5.

**Service Logic:**
```python
def calculate_priority_score(task: Task, energy_level: int) -> float:
    """Score = (Impact * Urgency) / Energy Required"""
    if task.energy_required > energy_level:
        return 0.0  # Suppressed
    return (task.impact * task.urgency) / task.energy_required
```

**LLM Integration (Google Gemini):**
- Entity Extraction: When a task is ingested, call Gemini to extract:
  title, impact (1-5), urgency (1-5), energy_required (1-5), is_big_rock
- Task Breakdown: When user clicks "Break Down", call Gemini for 3 concrete sub-steps

**Endpoints:**
```
POST /agent/rank              - Re-rank all tasks for current user + energy
POST /agent/extract           - Run entity extraction on raw text (called by ingestor)
POST /agent/breakdown/{task_id} - Generate 3 sub-steps for a task
```

---

### Module 6: Single-Card Interface (Focus UX)

**Description:** The main app experience. Shows exactly ONE Cloud Gray task card at a time against a Deep Slate background. No lists, no sidebar, no notifications visible.

**Pages:**
```
/focus  - The Single-Card Interface:
          - Deep Slate full-screen background
          - One Cloud Gray card: task title + description
          - Soft Mint "Start" button (marks task in-progress)
          - Muted Amber "Break Down" button (triggers LLM breakdown)
          - Soft Mint "Done" button (appears after Start clicked)
          - Ghost "Skip" button (re-ranks and shows next task)
          - Framer Motion card slide-in animation on task transition
          - Big Rock tasks: Muted Amber glow border on card
```

**Logic:**
- On load: call GET /tasks/next with current energy level
- On "Break Down": call POST /agent/breakdown/{task_id}, show sub-steps inline
- On "Done": call POST /tasks/{id}/complete, animate card out, load next
- On "Skip": re-fetch next task

---

### Module 7: Fresh Start Protocol (Shame-Gate)

**Description:** A compassionate logic trigger. When the system detects the user has been absent for more than 18 hours, instead of showing overdue red alerts, it presents a full-screen calming Soft Mint "Reset" prompt. Stale tasks are silently archived.

**Models:**
```
FreshStartLog:
  - id, user_id (FK), triggered_at
  - tasks_archived_count, next_action_task_id
```

**Endpoints:**
```
GET  /freshstart/check    - Check if Fresh Start should trigger
POST /freshstart/reset    - Archive stale tasks, force one "Next Best Action"
GET  /freshstart/history  - Log of past resets
```

**Pages:**
```
/fresh-start  - The Fresh Start screen:
                - Full-screen Deep Slate with Soft Mint accents
                - NO red text, NO "overdue" language
                - Message: "Welcome back. Everything's been cleared.
                            What's ONE thing you can do right now?"
                - Single recommended task (lowest energy, highest score)
                - CTA: "Let's do this" → /focus
```

**Logic:**
- On app load: always call GET /freshstart/check first
- If triggered: redirect to /fresh-start before /check-in

---

### Module 8: Analytics Dashboard

**Description:** Visualize energy patterns and task completion over time. Helps users understand their executive function rhythms.

**Models:**
```
DailyStats:
  - id, user_id (FK), date
  - avg_energy_level, tasks_completed, tasks_archived
  - big_rocks_completed, easy_wins_completed
  - fresh_starts_triggered
```

**Endpoints:**
```
GET /analytics/summary          - Last 7 days summary
GET /analytics/trends           - 30-day energy and completion trends
GET /analytics/completion-rate  - Overall task completion percentage
```

**Pages:**
```
/analytics  - Analytics Dashboard:
              - Energy level trend chart (line, Soft Mint color)
              - Tasks completed per day (bar chart)
              - Big Rocks vs Easy Wins ratio
              - Fresh Start triggers count
              - Recharts on Deep Slate background
```

---

### Module 9: Admin Panel

**Description:** Internal admin interface for platform management.

**Endpoints:**
```
GET /admin/users          - List all users with stats
PUT /admin/users/{id}     - Update user status
GET /admin/stats          - Platform-wide statistics
GET /admin/integrations   - Integration health overview
GET /admin/sync-logs      - Recent sync activity
```

**Pages:**
```
/admin         - Admin dashboard (admin-only)
/admin/users   - User management table
```

---

## ACCEPTANCE CRITERIA

### Authentication
- [ ] User can register with email/password
- [ ] User can login with email/password
- [ ] Google OAuth login works end-to-end
- [ ] JWT access + refresh tokens work correctly
- [ ] Protected routes redirect to login if unauthenticated

### Integrations
- [ ] User can connect Gmail via OAuth
- [ ] User can connect Slack via OAuth
- [ ] User can connect Notion via OAuth
- [ ] Background sync imports unresolved items every 30 minutes
- [ ] Duplicate detection prevents re-importing same items
- [ ] User can disconnect any integration

### Task Management
- [ ] Tasks ingested from all sources appear in the system
- [ ] LLM correctly extracts impact, urgency, energy_required
- [ ] Manual task creation works
- [ ] Tasks can be completed, snoozed, or archived

### Bandwidth Sensor
- [ ] Energy slider (1-5) renders correctly on /check-in
- [ ] Energy level is logged per session
- [ ] Glowing Soft Mint visual effect renders correctly

### Executive Function Agent
- [ ] Priority score: (Impact * Urgency) / Energy Required
- [ ] Tasks with energy_required > user_level are suppressed
- [ ] /tasks/next returns correct highest-priority task
- [ ] Task breakdown returns 3 concrete sub-steps

### Single-Card Interface
- [ ] Exactly one task card shows at a time
- [ ] Start, Break Down, Done, Skip buttons all function
- [ ] Card transitions animate smoothly
- [ ] Big Rock tasks show Muted Amber glow

### Fresh Start Protocol
- [ ] System detects absences > 18 hours
- [ ] Fresh Start screen shows instead of overdue alerts
- [ ] Stale tasks are archived (not deleted)
- [ ] User is guided to one "Next Best Action"

### Analytics
- [ ] Energy trend chart shows last 30 days
- [ ] Task completion chart renders correctly

### Quality
- [ ] All API endpoints in OpenAPI/Swagger
- [ ] Backend test coverage 80%+
- [ ] Frontend TypeScript strict mode passes
- [ ] Docker build succeeds
- [ ] All secrets in environment variables

---

## SPECIAL REQUIREMENTS

### Security
- [x] Rate limiting on auth endpoints (slowapi)
- [x] Input validation on all endpoints (Pydantic)
- [x] OAuth tokens stored encrypted in database
- [x] CSRF protection for OAuth flows

### Integrations
- [x] Gmail API (Google Cloud Console, read-only scope)
- [x] Slack API (OAuth 2.0, channels:history, im:history)
- [x] Notion API (OAuth, read pages and databases)
- [x] Google Gemini API (entity extraction + task breakdown)

### Background Processing
- [x] APScheduler for periodic sync jobs
- [x] Sync every 30 minutes per active integration
- [x] Failed syncs logged to SyncLog with error details

---

## AGENTS

| Agent | Role | Works On |
|-------|------|----------|
| DATABASE-AGENT | Creates all models and migrations | User, Task, Integration, EnergyLog, FreshStartLog, DailyStats |
| BACKEND-AGENT | Builds API endpoints and services | All modules' backends |
| FRONTEND-AGENT | Creates UI pages and components | All modules' frontends |
| DEVOPS-AGENT | Sets up Docker, CI/CD, environments | Infrastructure |
| TEST-AGENT | Writes unit and integration tests | All code |
| REVIEW-AGENT | Security and code quality audit | All code |

---

# READY?

```bash
/generate-prp INITIAL.md
```

Then:

```bash
/execute-prp PRPs/sift-prp.md
```
