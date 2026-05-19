import { ROOMS, ROSTER } from '@/data/content';
import type { Find, GameState, Lock, RoomId, SpotState } from './types';

export function freshState(): GameState {
  const empty = <T,>(v: T): Record<RoomId, T> => ({
    1: structuredClone(v),
    2: structuredClone(v),
    3: structuredClone(v),
    4: structuredClone(v),
  });
  return {
    v: 3,
    order: ROSTER.slice(),
    turnPos: 0,
    found: empty([] as string[]),
    solved: empty([] as string[]),
    rooms: empty({} as Record<string, number>),
    lifelines: empty({} as Record<string, true>),
    helper: { 1: null, 2: null, 3: null, 4: null },
    completed: { 1: false, 2: false, 3: false, 4: false },
  };
}

export function curP(s: GameState): string {
  const o = s.order.length ? s.order : ROSTER;
  return o[s.turnPos % o.length];
}

export function nextP(s: GameState): string {
  const o = s.order.length ? s.order : ROSTER;
  return o[(s.turnPos + 1) % o.length];
}

export function addPts(s: GameState, room: RoomId, player: string, pts: number): void {
  s.rooms[room][player] = (s.rooms[room][player] || 0) + pts;
}

export function roomTotals(s: GameState, room: RoomId): Record<string, number> {
  const t: Record<string, number> = {};
  ROSTER.forEach((p) => {
    t[p] = s.rooms[room][p] || 0;
  });
  return t;
}

export function cumulative(s: GameState): Record<string, number> {
  const t: Record<string, number> = {};
  ROSTER.forEach((p) => {
    t[p] = 0;
    for (let w = 1; w <= 4; w++) t[p] += s.rooms[w as RoomId][p] || 0;
  });
  return t;
}

export interface Ranked {
  p: string;
  v: number;
  rank: number;
}

export function ranked(tot: Record<string, number>): Ranked[] {
  const arr: Ranked[] = ROSTER.map((p) => ({ p, v: tot[p] ?? 0, rank: 0 })).sort(
    (a, b) => b.v - a.v || a.p.localeCompare(b.p),
  );
  let rank = 0;
  let last: number | null = null;
  let seen = 0;
  arr.forEach((x) => {
    seen++;
    if (last === null || x.v !== last) {
      rank = seen;
      last = x.v;
    }
    x.rank = rank;
  });
  return arr;
}

export function medal(r: number): string {
  return r === 1 ? '🥇' : r === 2 ? '🥈' : r === 3 ? '🥉' : String(r);
}

export function fmt(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

export type SpotInput =
  | (Find & { type: 'find' })
  | (Lock & { type: 'lock' });

export function spotState(s: GameState, rm: RoomId, item: SpotInput): SpotState {
  const found = s.found[rm];
  const solved = s.solved[rm];
  const R = ROOMS[rm - 1];

  if (item.type === 'find') {
    const done = found.includes(item.id) || found.includes('_d_' + item.id);
    return {
      cls: done ? 'done' : 'hunt',
      glyph: item.glyph ?? '?',
      sub: done ? (item.decoy ? 'Nothing' : 'Found ✓') : 'Answer',
    };
  }
  const reqMet = !item.requires || found.includes(item.requires);
  if (solved.includes(item.id)) {
    return {
      cls: 'open',
      glyph: item.exit ? '🚪' : '🔓',
      sub: item.exit ? 'Open!' : 'Cracked ✓',
    };
  }
  if (item.exit) {
    const allOther = R.locks.filter((l) => !l.exit).every((l) => solved.includes(l.id));
    if (!allOther || !reqMet)
      return { cls: 'sealed', glyph: '🚪', sub: 'Sealed' };
    return { cls: 'live', glyph: '🚪', sub: 'Final lock' };
  }
  if (!reqMet) return { cls: 'sealed', glyph: '❓', sub: 'Locked' };
  return { cls: 'live', glyph: '🔒', sub: 'Crack it' };
}

export interface PayoutEntry {
  player: string;
  questPts: number;
  rank: number;
  bonus: number;
  awardco: number;
}

export function payout(s: GameState): PayoutEntry[] {
  const tot = cumulative(s);
  const arr = ranked(tot);
  return arr.map((x) => {
    const bonus = x.rank === 1 ? 10 : x.rank === 2 ? 5 : x.rank === 3 ? 2 : 0;
    return {
      player: x.p,
      questPts: x.v,
      rank: x.rank,
      bonus,
      awardco: 5 + bonus,
    };
  });
}

/* ===== resolvers (pure, take state and return new state) ===== */

export function passTurn(s: GameState): GameState {
  return { ...s, turnPos: s.turnPos + 1 };
}

export function tapDecoy(s: GameState, rm: RoomId, id: string): GameState {
  const next = structuredClone(s);
  const mark = '_d_' + id;
  if (!next.found[rm].includes(mark)) next.found[rm].push(mark);
  next.turnPos += 1;
  return next;
}

export interface ResolveInput {
  rm: RoomId;
  itemId: string;
  isClue: boolean;
  correct: boolean;
}

export function resolveChallenge(s: GameState, input: ResolveInput): GameState {
  const next = structuredClone(s);
  const act = curP(next);
  const helper = next.helper[input.rm];
  if (helper) {
    next.lifelines[input.rm][act] = true;
    if (input.correct) {
      addPts(next, input.rm, act, 0.5);
      addPts(next, input.rm, helper, 0.5);
    }
  } else if (input.correct) {
    addPts(next, input.rm, act, 1);
  }
  if (input.correct) {
    if (input.isClue) {
      if (!next.found[input.rm].includes(input.itemId)) next.found[input.rm].push(input.itemId);
    } else {
      if (!next.solved[input.rm].includes(input.itemId))
        next.solved[input.rm].push(input.itemId);
    }
  }
  next.helper[input.rm] = null;
  next.turnPos += 1;
  return next;
}

export function shuffleOrder(s: GameState, rm: RoomId, rng: () => number = Math.random): GameState {
  const next = structuredClone(s);
  const o = next.order.slice();
  for (let i = o.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [o[i], o[j]] = [o[j], o[i]];
  }
  next.order = o;
  next.turnPos = 0;
  next.helper[rm] = null;
  return next;
}

export function pickPlayer(s: GameState, rm: RoomId, p: string): GameState {
  const next = structuredClone(s);
  const idx = next.order.indexOf(p);
  if (idx < 0) return s;
  next.turnPos = idx;
  if (next.helper[rm] === p) next.helper[rm] = null;
  return next;
}

export function setHelper(s: GameState, rm: RoomId, p: string): GameState {
  const next = structuredClone(s);
  next.helper[rm] = p;
  return next;
}

export function finishRoom(s: GameState, rm: RoomId): GameState {
  const next = structuredClone(s);
  next.completed[rm] = true;
  return next;
}

export function migrate(maybe: any): GameState {
  if (!maybe || typeof maybe !== 'object') return freshState();
  const base = freshState();
  const out: GameState = {
    ...base,
    ...maybe,
    v: 3,
    order: Array.isArray(maybe.order) && maybe.order.length ? maybe.order : ROSTER.slice(),
    turnPos: typeof maybe.turnPos === 'number' ? maybe.turnPos : 0,
    found: { ...base.found, ...(maybe.found ?? {}) },
    solved: { ...base.solved, ...(maybe.solved ?? {}) },
    rooms: { ...base.rooms, ...(maybe.rooms ?? {}) },
    lifelines: { ...base.lifelines, ...(maybe.lifelines ?? {}) },
    helper: { ...base.helper, ...(maybe.helper ?? {}) },
    completed: { ...base.completed, ...(maybe.completed ?? {}) },
  };
  return out;
}
