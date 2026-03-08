# Manual Task Creation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a floating `+` button on FocusPage that opens a minimal modal for creating tasks; Gemini auto-infers impact/urgency/energy from the title and description.

**Architecture:** Backend makes `TaskCreate` fields optional and calls the existing `extract_task_entities()` Gemini service when they're omitted. Frontend adds an `AddTaskModal` component and a FAB on FocusPage; a brief toast confirms success before re-fetching the next task.

**Tech Stack:** FastAPI + Pydantic (backend), React + TypeScript + Framer Motion + Tailwind (frontend), existing `gemini_service.extract_task_entities`, existing `taskService.create`

---

### Task 1: Make TaskCreate fields optional + wire Gemini in create_task

**Files:**
- Modify: `backend/app/schemas/task.py:6-18`
- Modify: `backend/app/routers/tasks.py:36-57`

**Step 1: Write the failing test**

Create `backend/tests/test_task_create_gemini.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app

# Minimal auth bypass — reuse pattern from any existing test if present
HEADERS = {}  # will be set after login in fixture below

@pytest.fixture
async def auth_headers(async_client: AsyncClient):
    reg = await async_client.post("/api/v1/auth/register", json={
        "email": "tasktest@example.com",
        "password": "TestPass123!",
        "full_name": "Task Tester"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_task_without_ratings_calls_gemini(auth_headers):
    """When impact/urgency/energy_required are omitted, Gemini should be called."""
    fake_entities = {
        "title": "Write report",
        "impact": 4,
        "urgency": 3,
        "energy_required": 2,
        "is_big_rock": False,
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch(
            "app.routers.tasks.extract_task_entities",
            new=AsyncMock(return_value=fake_entities)
        ) as mock_gemini:
            resp = await client.post(
                "/api/v1/tasks",
                json={"title": "Write report", "description": "quarterly report"},
                headers=auth_headers,
            )
    assert resp.status_code == 201
    data = resp.json()
    assert data["impact"] == 4
    assert data["urgency"] == 3
    assert data["energy_required"] == 2
    mock_gemini.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_with_explicit_ratings_skips_gemini(auth_headers):
    """When all ratings are provided, Gemini should NOT be called."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch(
            "app.routers.tasks.extract_task_entities",
            new=AsyncMock()
        ) as mock_gemini:
            resp = await client.post(
                "/api/v1/tasks",
                json={"title": "Manual task", "impact": 2, "urgency": 2, "energy_required": 1},
                headers=auth_headers,
            )
    assert resp.status_code == 201
    assert resp.json()["impact"] == 2
    mock_gemini.assert_not_called()
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_task_create_gemini.py -v
```
Expected: FAIL — `extract_task_entities` is not imported in router, and fields are required.

**Step 3: Update `TaskCreate` schema to make ratings optional**

In `backend/app/schemas/task.py`, change:
```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    impact: Optional[int] = None      # was: int = 3
    urgency: Optional[int] = None     # was: int = 3
    energy_required: Optional[int] = None  # was: int = 3

    @field_validator("impact", "urgency", "energy_required", mode="before")
    @classmethod
    def validate_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Value must be between 1 and 5")
        return v
```

**Step 4: Update `create_task` router to call Gemini when ratings are missing**

In `backend/app/routers/tasks.py`, add the import at the top of the file (after existing imports):
```python
from app.services.gemini_service import generate_task_breakdown, extract_task_entities
```

Replace the `create_task` function body (lines 42-57) with:
```python
    from app.services.ranking_service import is_big_rock, calculate_priority_score

    impact = task_data.impact
    urgency = task_data.urgency
    energy_required = task_data.energy_required

    # If any ratings are missing, ask Gemini to infer them
    if impact is None or urgency is None or energy_required is None:
        combined = task_data.title
        if task_data.description:
            combined += f"\n{task_data.description}"
        entities = await extract_task_entities(combined)
        impact = impact if impact is not None else entities["impact"]
        urgency = urgency if urgency is not None else entities["urgency"]
        energy_required = energy_required if energy_required is not None else entities["energy_required"]

    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        source="manual",
        impact=impact,
        urgency=urgency,
        energy_required=energy_required,
    )
    task.is_big_rock = is_big_rock(task)
    task.priority_score = calculate_priority_score(task, energy_level=3)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
```

**Step 5: Run tests to verify they pass**

```bash
cd backend && pytest tests/test_task_create_gemini.py -v
```
Expected: PASS (both tests green)

**Step 6: Commit**

```bash
git add backend/app/schemas/task.py backend/app/routers/tasks.py backend/tests/test_task_create_gemini.py
git commit -m "feat: make TaskCreate ratings optional, infer via Gemini when omitted"
```

---

### Task 2: Add `createTask` to `useTasks` hook

**Files:**
- Modify: `frontend/src/hooks/useTasks.ts`

The `taskService.create` already exists. We just expose it through the hook so FocusPage doesn't import the service directly.

**Step 1: Add `createTask` to the hook**

In `frontend/src/hooks/useTasks.ts`, add after the `breakdownTask` callback (before the return statement):

```typescript
const createTask = useCallback(async (title: string, description?: string): Promise<void> => {
  await taskService.create({ title, description })
}, [])
```

Add `createTask` to the return object:
```typescript
return {
  task,
  eligibleTasks,
  isLoading,
  error,
  fetchNext,
  fetchEligible,
  selectTask,
  completeTask,
  snoozeTask,
  breakdownTask,
  createTask,
}
```

**Step 2: Verify TypeScript compiles**

```bash
cd frontend && npm run type-check
```
Expected: no errors

**Step 3: Commit**

```bash
git add frontend/src/hooks/useTasks.ts
git commit -m "feat: expose createTask in useTasks hook"
```

---

### Task 3: Build `AddTaskModal` component

**Files:**
- Create: `frontend/src/components/AddTaskModal/AddTaskModal.tsx`

**Step 1: Create the component**

```tsx
import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AddTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (title: string, description?: string) => Promise<void>
}

export function AddTaskModal({ isOpen, onClose, onSubmit }: AddTaskModalProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const titleRef = useRef<HTMLInputElement>(null)

  // Autofocus title when modal opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => titleRef.current?.focus(), 50)
    } else {
      setTitle('')
      setDescription('')
      setError(null)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit(title.trim(), description.trim() || undefined)
      onClose()
    } catch {
      setError('Failed to add task. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-deep-slate/80 z-40 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-50 px-4 pb-8 sm:bottom-auto sm:top-1/2 sm:-translate-y-1/2 sm:max-w-lg sm:mx-auto"
          >
            <form
              onSubmit={handleSubmit}
              className="bg-cloud-gray rounded-2xl p-6 shadow-2xl"
            >
              <h2 className="text-deep-slate font-bold text-lg mb-1">Add a task</h2>
              <p className="text-slate-500 text-sm mb-4">
                Sift will figure out the priority automatically.
              </p>

              <input
                ref={titleRef}
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="What needs doing?"
                required
                className="w-full bg-white/70 text-deep-slate placeholder-slate-400
                           rounded-xl px-4 py-3 mb-3 outline-none
                           focus:ring-2 focus:ring-soft-mint transition-all"
              />

              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional — helps Sift rank it better"
                rows={3}
                className="w-full bg-white/70 text-deep-slate placeholder-slate-400
                           rounded-xl px-4 py-3 mb-4 outline-none resize-none
                           focus:ring-2 focus:ring-soft-mint transition-all"
              />

              {error && (
                <p className="text-muted-amber text-sm mb-3">{error}</p>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 py-3 rounded-xl text-slate-500 font-medium
                             hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!title.trim() || isSubmitting}
                  className="flex-1 py-3 rounded-xl bg-soft-mint text-deep-slate font-semibold
                             hover:brightness-105 transition-all
                             disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Adding…' : 'Add Task'}
                </button>
              </div>
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

**Step 2: Verify TypeScript compiles**

```bash
cd frontend && npm run type-check
```
Expected: no errors

**Step 3: Commit**

```bash
git add frontend/src/components/AddTaskModal/AddTaskModal.tsx
git commit -m "feat: add AddTaskModal component"
```

---

### Task 4: Add FAB + toast + wire modal into FocusPage

**Files:**
- Modify: `frontend/src/pages/FocusPage.tsx`

**Step 1: Update FocusPage**

Add the following imports at the top of `FocusPage.tsx` (after existing imports):

```typescript
import { AddTaskModal } from '../components/AddTaskModal/AddTaskModal'
```

Add modal and toast state inside the component (after the existing `useState` declarations):

```typescript
const [showAddModal, setShowAddModal] = useState(false)
const [toast, setToast] = useState<string | null>(null)
```

Destructure `createTask` from `useTasks`:

```typescript
const {
  task,
  isLoading,
  error,
  fetchNext,
  fetchEligible,
  completeTask,
  snoozeTask,
  breakdownTask,
  createTask,
} = useTasks(confirmedEnergy ?? 3)
```

Add a toast helper after the state declarations:

```typescript
const showToast = (msg: string) => {
  setToast(msg)
  setTimeout(() => setToast(null), 3000)
}
```

Add the submit handler:

```typescript
const handleAddTask = async (title: string, description?: string) => {
  await createTask(title, description)
  showToast('Task added')
  await fetchNext()
  await fetchEligible()
}
```

**Step 2: Add FAB and modal to the FOCUSED render path**

In the `FOCUSED` state return block, wrap the existing JSX in a fragment and append the FAB, modal, and toast. The FAB should only appear when `appState === 'FOCUSED'` (it's already inside that branch). Add just before the closing `</AppLayout>` tag:

```tsx
          {/* Floating Add Button */}
          <button
            onClick={() => setShowAddModal(true)}
            className="fixed bottom-8 right-6 w-14 h-14 rounded-full bg-soft-mint
                       text-deep-slate text-2xl font-bold shadow-lg
                       hover:brightness-105 active:scale-95 transition-all z-30
                       flex items-center justify-center"
            aria-label="Add task"
          >
            +
          </button>

          {/* Toast */}
          <AnimatePresence>
            {toast && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="fixed bottom-28 left-1/2 -translate-x-1/2 z-50
                           bg-soft-mint text-deep-slate text-sm font-semibold
                           px-5 py-2 rounded-full shadow-lg"
              >
                {toast}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Add Task Modal */}
          <AddTaskModal
            isOpen={showAddModal}
            onClose={() => setShowAddModal(false)}
            onSubmit={handleAddTask}
          />
```

Also add the same modal (but not the FAB) to the `noMoreTasks` empty state so users can add tasks from there too — place the `<AddTaskModal>` and its trigger alongside the "Adjust energy" button:

```tsx
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-soft-mint/20 text-soft-mint font-semibold px-6 py-3
                           rounded-xl hover:bg-soft-mint/30 transition-all"
              >
                + Add a task
              </button>
```

**Step 3: Verify TypeScript compiles and lint passes**

```bash
cd frontend && npm run type-check && npm run lint
```
Expected: no errors

**Step 4: Commit**

```bash
git add frontend/src/pages/FocusPage.tsx
git commit -m "feat: add floating + button and AddTaskModal to FocusPage"
```

---

### Task 5: Smoke test end-to-end in Docker

**Step 1: Rebuild and restart containers**

```bash
cd /home/ubuntu/Projects/Sift
sudo docker compose up -d --build
```

**Step 2: Verify backend health**

```bash
curl -s http://localhost:8001/health | python3 -m json.tool
```
Expected: `{"status": "healthy", ...}`

**Step 3: Manual smoke test**

1. Open https://sift-app.loca.lt
2. Log in
3. Complete the energy check-in
4. Verify the `+` FAB appears bottom-right
5. Click `+` — modal slides up, title input is autofocused
6. Enter a title (e.g. "Write project report") and optional description
7. Click "Add Task" — modal closes, green toast "Task added" appears briefly
8. Next task re-fetches (may be the new task or an existing one based on ranking)
9. Press Escape key on open modal — modal should close

**Step 4: Verify empty state also has add button**

On the energy check-in page, set energy to 1 if no low-energy tasks exist — verify the "all clear" state shows "+ Add a task" button which also opens the modal.

---

## Summary of Files Changed

| File | Change |
|------|--------|
| `backend/app/schemas/task.py` | `impact/urgency/energy_required` → `Optional[int] = None` |
| `backend/app/routers/tasks.py` | Import + call `extract_task_entities` when ratings are `None` |
| `backend/tests/test_task_create_gemini.py` | New test file |
| `frontend/src/hooks/useTasks.ts` | Add `createTask` callback |
| `frontend/src/components/AddTaskModal/AddTaskModal.tsx` | New component |
| `frontend/src/pages/FocusPage.tsx` | Wire in FAB, modal, toast |
