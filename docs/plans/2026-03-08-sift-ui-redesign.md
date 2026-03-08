# Sift UI Redesign — Design Document
**Date:** 2026-03-08
**Branch:** ui_changes
**Approach:** Option A — Surgical component replacement

---

## Overview

Neuroinclusive redesign of the Sift frontend. Goal: eliminate choice paralysis and reduce cognitive load for ADHD users. All existing hooks, services, routing, and auth remain untouched. Only the visual layer changes.

---

## Section 1: EnergyGate Component

**Replaces:** `frontend/src/components/EnergySlider/EnergySlider.tsx`

Three large tap-target cards replacing the 5-button numeric slider.

| Card | Icon | Label | Sub-label | API Value |
|------|------|-------|-----------|-----------|
| 1 | 🌊 | Low | "Gentle tasks only" | `2` |
| 2 | ⚡ | Mid | "Steady and present" | `3` |
| 3 | 🔥 | High | "Ready to tackle anything" | `5` |

- Vertical stack on mobile, row on ≥640px
- Card height: ~140px, full-width mobile / 1/3 desktop
- Selected: `scale(1.05)` + Soft Mint `#B2D8C8` border glow (spring physics)
- Unselected: `opacity: 0.5`
- On confirm: gate exits `{ y: -40, opacity: 0 }`, task card springs in from below
- No numeric scale exposed to the user

---

## Section 2: TaskCard Overhaul

**File:** `frontend/src/components/TaskCard/TaskCard.tsx`
Same props interface, full visual replacement.

### Inverted Hierarchy (top → bottom)
1. **Micro-step** — `text-3xl font-bold text-off-white` — largest element (first sub_step, or task title if none)
2. **Main task title** — `text-sm text-muted-text` — visually demoted, sits below micro-step
3. Source badge + Big Rock indicator — smallest, top-right corner

### Visual Progress Ring
- SVG circle, 80px diameter
- Soft Mint `#B2D8C8` stroke animates `strokeDashoffset` from 0 to full over 60 minutes
- Ring track: `opacity-20` white on Deep Slate background — no digits
- Pulsing dot at ring head indicates motion without ticking

### Swipe-to-Snooze / Swipe-to-Complete
- `drag="x"` with `useDragControls`
- Drag right >80px → snooze (60 min), `💤` ghost label fades in at right edge
- Drag left >80px → complete, `✓` ghost label at left edge
- Spring snap-back if threshold not met — `dragElastic: 0.15`

### Break Down Button
- Muted Amber `#E2B07E`, visible on all tasks (not just Big Rocks)
- Click → `atomizing` state: background pulses amber, 3 skeleton lines animate in sequence
- After AI response: 3 sub-steps appear, micro-step updates to `sub_steps[0]`

---

## Section 3: FocusPage Orchestration

**File:** `frontend/src/pages/FocusPage.tsx`

### State Machine
```
ENERGY_GATE → FOCUSED → FOCUS_MODE
                ↓
           (FreshStartPage guards entry if gap > 18h)
```

### Focus Mode — Breathing Background (State C)
- Background pulses `#1A1C2E` ↔ `#1E2235` at ~4s cycle
- `repeat: Infinity, repeatType: "mirror"` via Framer Motion
- All nav/layout chrome hidden — pure fullscreen card
- Tap-outside or `ESC` exits breathing, returns to FOCUSED

### AppLayout Suppression
- `FocusPage` signals fullscreen mode to hide sidebar/nav during FOCUS_MODE
- All other states retain nav

---

## Section 4: FreshStartPage Polish

**File:** `frontend/src/pages/FreshStartPage.tsx`

- Replace emoji-heavy header with large text: *"You've been away. Let's not carry yesterday's weight."*
- CTA button: **"Clear & Begin"** in Soft Mint — no red anywhere
- Archived count: neutral gray pill `"23 tasks cleared"` — no guilt framing
- Smooth fade-in entrance animation

---

## Color Tokens (this redesign)

| Token | Hex | Usage |
|-------|-----|-------|
| Deep Slate | `#1A1C2E` | All backgrounds |
| Soft Mint | `#B2D8C8` | Primary CTA, progress ring, selected state |
| Muted Amber | `#E2B07E` | Break Down button, Big Rock badge |
| Off White | `#F8FAFC` | Primary text (micro-step) |
| Muted Text | `#94A3B8` | Secondary text (main task title) |

---

## Files Changed

| File | Change |
|------|--------|
| `components/EnergySlider/EnergySlider.tsx` | Replace with 3-card EnergyGate |
| `components/TaskCard/TaskCard.tsx` | Inverted hierarchy + ring + swipe |
| `pages/FocusPage.tsx` | Breathing focus mode + state machine |
| `pages/FreshStartPage.tsx` | Copy + style polish |
| `index.css` | Add breathing animation keyframes if needed |

## Files NOT Changed

- All hooks (`useTasks`, `useEnergy`, `useFreshStart`, `useIntegrations`)
- All services (`api.ts`, `taskService.ts`, `energyService.ts`)
- `AuthContext.tsx`, `ProtectedRoute.tsx`, `AppLayout.tsx`
- `App.tsx`, routing, `types/index.ts`
- Backend — zero changes
