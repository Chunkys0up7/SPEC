import { describe, it, expect } from 'vitest';
import { ROOMS } from '../../src/data/content';
import { freshState, spotState } from '../../src/game/logic';

describe('spotState gating', () => {
  it('a fresh clue is hunt', () => {
    const s = freshState();
    const sticky = ROOMS[0].finds.find((f) => f.id === 'sticky')!;
    expect(spotState(s, 1, { ...sticky, type: 'find' }).cls).toBe('hunt');
  });

  it('a found clue is done', () => {
    const s = freshState();
    s.found[1].push('sticky');
    const sticky = ROOMS[0].finds.find((f) => f.id === 'sticky')!;
    expect(spotState(s, 1, { ...sticky, type: 'find' }).cls).toBe('done');
  });

  it('a tapped decoy is done (nothing)', () => {
    const s = freshState();
    s.found[1].push('_d_mug');
    const mug = ROOMS[0].finds.find((f) => f.id === 'mug')!;
    expect(spotState(s, 1, { ...mug, type: 'find' }).cls).toBe('done');
  });

  it('lock with unmet requirement is sealed', () => {
    const s = freshState();
    const lk2 = ROOMS[0].locks.find((l) => l.id === 'lk2')!; // requires "poster"
    expect(spotState(s, 1, { ...lk2, type: 'lock' }).cls).toBe('sealed');
  });

  it('lock with requirement met becomes live', () => {
    const s = freshState();
    s.found[1].push('poster');
    const lk2 = ROOMS[0].locks.find((l) => l.id === 'lk2')!;
    expect(spotState(s, 1, { ...lk2, type: 'lock' }).cls).toBe('live');
  });

  it('a solved lock is open', () => {
    const s = freshState();
    s.solved[1].push('lk2');
    const lk2 = ROOMS[0].locks.find((l) => l.id === 'lk2')!;
    expect(spotState(s, 1, { ...lk2, type: 'lock' }).cls).toBe('open');
  });

  it('exit stays sealed if not all other locks solved', () => {
    const s = freshState();
    // Solve only 4 of 5 non-exit locks
    s.solved[1] = ['lk1', 'lk2', 'lk3', 'lk4'];
    s.found[1] = ['poster', 'drawer', 'sticky'];
    const exit = ROOMS[0].locks.find((l) => l.exit)!;
    expect(spotState(s, 1, { ...exit, type: 'lock' }).cls).toBe('sealed');
  });

  it('exit goes live when all non-exit locks solved and requires met', () => {
    const s = freshState();
    s.solved[1] = ['lk1', 'lk2', 'lk3', 'lk4', 'lk5'];
    const exit = ROOMS[0].locks.find((l) => l.exit)!;
    expect(spotState(s, 1, { ...exit, type: 'lock' }).cls).toBe('live');
  });

  it('Room 2 exit also requires the binder clue', () => {
    const s = freshState();
    s.solved[2] = ['lk1', 'lk2', 'lk3', 'lk4', 'lk5'];
    const exit = ROOMS[1].locks.find((l) => l.exit)!;
    // requires 'binder' — without it, still sealed
    expect(spotState(s, 2, { ...exit, type: 'lock' }).cls).toBe('sealed');
    s.found[2].push('binder');
    expect(spotState(s, 2, { ...exit, type: 'lock' }).cls).toBe('live');
  });

  it('every room has exactly 6 finds and 6 locks, with exactly one exit', () => {
    for (const R of ROOMS) {
      expect(R.finds).toHaveLength(6);
      expect(R.locks).toHaveLength(6);
      expect(R.locks.filter((l) => l.exit)).toHaveLength(1);
    }
  });
});
