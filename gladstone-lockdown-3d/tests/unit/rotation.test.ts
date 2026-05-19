import { describe, it, expect } from 'vitest';
import { ROSTER } from '../../src/data/content';
import { curP, nextP, freshState, pickPlayer, shuffleOrder, passTurn } from '../../src/game/logic';

describe('turn rotation', () => {
  it('starts at first player', () => {
    const s = freshState();
    expect(curP(s)).toBe(ROSTER[0]);
    expect(nextP(s)).toBe(ROSTER[1]);
  });

  it('passes the turn continuously', () => {
    let s = freshState();
    for (let i = 0; i < ROSTER.length; i++) {
      expect(curP(s)).toBe(ROSTER[i % ROSTER.length]);
      s = passTurn(s);
    }
    expect(curP(s)).toBe(ROSTER[0]);
  });

  it('pick jumps the turn to that player', () => {
    let s = freshState();
    s = pickPlayer(s, 1, ROSTER[5]);
    expect(curP(s)).toBe(ROSTER[5]);
    expect(nextP(s)).toBe(ROSTER[6]);
  });

  it('pick clears that player as helper if they were nominated', () => {
    let s = freshState();
    s.helper[1] = ROSTER[3];
    s = pickPlayer(s, 1, ROSTER[3]);
    expect(s.helper[1]).toBeNull();
  });

  it('shuffleOrder resets turnPos to 0 and clears helper for the room', () => {
    let s = freshState();
    s.turnPos = 7;
    s.helper[2] = ROSTER[4];
    s = shuffleOrder(s, 2, () => 0.5);
    expect(s.turnPos).toBe(0);
    expect(s.helper[2]).toBeNull();
    expect(s.order).toHaveLength(ROSTER.length);
  });

  it('shuffleOrder produces a permutation of ROSTER', () => {
    let s = freshState();
    s = shuffleOrder(s, 1, () => 0.123);
    expect(new Set(s.order)).toEqual(new Set(ROSTER));
  });

  it('turn wraps around the order modulo length', () => {
    let s = freshState();
    s.turnPos = ROSTER.length * 3 + 2;
    expect(curP(s)).toBe(ROSTER[2]);
    expect(nextP(s)).toBe(ROSTER[3]);
  });
});
