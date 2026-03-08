# Manual Task Creation — Design Doc

**Date:** 2026-03-08
**Feature:** Add tasks directly from the UI via a floating action button on FocusPage

---

## Overview

Users can create tasks manually without relying on Gmail/Slack/Notion integrations. A floating `+` button on FocusPage opens a minimal modal. The user enters a title and optional description; Gemini infers impact, urgency, and energy_required automatically. After submission, a toast confirms success and Sift re-fetches the next ranked task.

---

## Architecture

### Backend

- **File:** `backend/app/schemas/task.py` — make `impact`, `urgency`, `energy_required` optional (`Optional[int] = None`) in `TaskCreate`
- **File:** `backend/app/routers/tasks.py` — in `create_task`, if any of those fields are `None`, call `gemini_service.extract_task_entities(title, description)` to fill them; fall back to `3` if Gemini fails
- **File:** `backend/app/services/gemini_service.py` — add `extract_task_entities(title, description) -> dict` returning `{impact, urgency, energy_required, is_big_rock}`

No new routes or migrations needed. The `POST /tasks` endpoint already sets `source="manual"`.

### Frontend

Three additions:

1. **`AddTaskModal` component** (`frontend/src/components/AddTaskModal/AddTaskModal.tsx`)
   - Semi-transparent Deep Slate overlay
   - Cloud Gray card, `rounded-2xl`
   - Autofocused title input (required)
   - Optional description textarea, placeholder: "optional — helps Sift rank it better"
   - Soft Mint submit button, disabled while loading
   - Error text in Muted Amber (never red)
   - Framer Motion: slide-up entry, fade-out exit

2. **Floating `+` FAB** added to FocusPage
   - Bottom-right corner, Soft Mint background, Deep Slate `+` icon
   - Visible in `FOCUSED` and no-tasks states
   - Hidden in `ENERGY_GATE` and `FOCUS_MODE` states

3. **Toast notification** — inline state in FocusPage, brief success/error message after submission

---

## UI Flow

```
FocusPage (FOCUSED state)
  └── FAB "+" (bottom-right)
        └── click → AddTaskModal slides up
              ├── Title (required)
              ├── Description (optional)
              ├── Cancel / Add Task
              └── submit
                    ├── POST /api/v1/tasks
                    ├── success → toast "Task added" → fetchNext()
                    └── error → Muted Amber error message in modal
```

---

## Error Handling

- Gemini failure → fall back to `impact=3, urgency=3, energy_required=3` silently
- Network error → display error in modal (Muted Amber), keep modal open
- Empty title → HTML5 `required` + disabled submit button

---

## Design Tokens

| Element | Token |
|---------|-------|
| FAB background | Soft Mint `#4ECCA3` |
| Modal overlay | Deep Slate `#0F172A` at 80% opacity |
| Modal card | Cloud Gray `#CBD5E1` |
| Submit button | Soft Mint `#4ECCA3` |
| Error text | Muted Amber `#F59E0B` |
| Input text | Deep Slate `#0F172A` |

---

## Out of Scope

- Manual rating sliders (Gemini handles this)
- Immediately surfacing the new task as current focus (Sift ranks it normally)
- Editing existing tasks from this modal
