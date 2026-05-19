# Gladstone Lockdown 3D

A 3D rebuild of the *Gladstone Lockdown* escape-room training game (originally
a single-file 2D HTML page), built with Vite + React + TypeScript +
react-three-fiber + Zustand.

The game logic, content, rotation, scoring and Awardco payout are **ported
verbatim** from the 2D version (`gladstone_lockdown.html`). Every question,
option, correct index, gating requirement and reward text matches the source.

## Quick start

```bash
cd gladstone-lockdown-3d
npm install
npm run dev          # http://localhost:5173

npm run test:run     # unit tests (Vitest)
npm run typecheck    # tsc --noEmit
npm run build        # production build
npm run e2e          # Playwright smoke tests (requires the browsers: npx playwright install)
```

## Project layout

```
src/
  data/content.ts         # ROOMS + ROSTER (verbatim port)
  game/
    types.ts              # Find / Lock / Room / GameState
    logic.ts              # rotation, scoring, gating, payout — pure, fully tested
    store.ts              # Zustand store with persist middleware
  scene/
    Room.tsx              # 3D room shell + object placement
    Lighting.tsx          # lamp, moonlight, fills
    Camera.tsx            # OrbitControls + focus-tween rig
    Furniture/Furniture.tsx  # single procedural component handling every ArtType
  ui/
    Hub.tsx               # 4 room cards + standings
    RoomView.tsx          # 3D canvas + inventory + escape CTA
    Challenge.tsx         # MC / code question overlay
    Dock.tsx              # turn bar, chips, action buttons
    Leaderboards.tsx      # per-room + cumulative + Awardco payout
    Header.tsx, HowTo.tsx, Toast.tsx
tests/
  unit/                   # rotation / scoring / gating / payout
  e2e/                    # Playwright smoke
```

## Mechanics (mirror the 2D source)

- **Turn rotation:** `turnPos` advances by 1 on every resolve (correct *or*
  wrong) and on every uncollected decoy tap.
- **Pick / shuffle:** `pick(player)` jumps `turnPos` to that player.
  `shuffleOrder` Fisher-Yates shuffles `order` and resets `turnPos = 0`.
- **Clue resolve:** correct → push `id` to `found[room]`, asker +1, turn +1.
  Wrong → no change, turn +1.
- **Lock resolve:** correct → push `id` to `solved[room]`, asker +1, turn +1.
  Wrong → no change, turn +1.
- **Decoy tap:** push `_d_<id>` to `found[room]`, no points, turn +1.
  Re-tapping a tapped decoy is a no-op.
- **Help lifeline:** one per asker per room. Correct → +0.5 to asker *and*
  helper; wrong → 0 to both. Lifeline locked either way, turn still advances.
- **Gating:** a lock with `requires` is `sealed` until that clue id is in
  `found[room]`. The exit lock is additionally sealed unless every non-exit
  lock id is in `solved[room]`.
- **Awardco:** everyone +5 base. Podium +10 / +5 / +2 by quest cumulative
  rank. Ties share rank; next rank skips by the count of tied players.

## Persistence

Zustand `persist` middleware → localStorage under
`gladstone_lockdown_3d_v1`. Migration from older `v < 3` shapes fills
missing fields with defaults. Reset wipes the key entirely.

## Keyboard shortcuts

- `Esc` close overlay · `R` reveal answer · `H` help lifeline
- `Y` correct · `N` wrong · `S` shuffle order
- `1`/`2`/`3`/`4` reserved for camera presets

## Accessibility

- `prefers-reduced-motion`: camera tweens, door animation, lock pulse all
  reduce to immediate updates.
- A collapsible list under each room exposes every interactive 3D object to
  keyboard / screen-reader users (no canvas-only paths).
- ARIA labels on overlay controls and modals; live-region toasts.
