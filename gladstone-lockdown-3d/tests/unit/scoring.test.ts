import { describe, it, expect } from 'vitest';
import { ROSTER } from '../../src/data/content';
import {
  freshState,
  resolveChallenge,
  tapDecoy,
  addPts,
  cumulative,
  ranked,
  setHelper,
} from '../../src/game/logic';

describe('scoring + resolve', () => {
  it('addPts accumulates points per room per player', () => {
    const s = freshState();
    addPts(s, 1, ROSTER[0], 1);
    addPts(s, 1, ROSTER[0], 0.5);
    expect(s.rooms[1][ROSTER[0]]).toBe(1.5);
  });

  it('correct lock awards +1 to the current player and advances the turn', () => {
    const s0 = freshState();
    const s1 = resolveChallenge(s0, { rm: 1, itemId: 'lk1', isClue: false, correct: true });
    expect(s1.rooms[1][ROSTER[0]]).toBe(1);
    expect(s1.turnPos).toBe(1);
    expect(s1.solved[1]).toContain('lk1');
  });

  it('wrong lock awards nothing and still advances the turn', () => {
    const s0 = freshState();
    const s1 = resolveChallenge(s0, { rm: 1, itemId: 'lk1', isClue: false, correct: false });
    expect(s1.rooms[1][ROSTER[0]] ?? 0).toBe(0);
    expect(s1.turnPos).toBe(1);
    expect(s1.solved[1]).not.toContain('lk1');
  });

  it('correct clue records the find and awards +1', () => {
    const s0 = freshState();
    const s1 = resolveChallenge(s0, { rm: 1, itemId: 'sticky', isClue: true, correct: true });
    expect(s1.found[1]).toContain('sticky');
    expect(s1.rooms[1][ROSTER[0]]).toBe(1);
  });

  it('wrong clue does not add to found', () => {
    const s0 = freshState();
    const s1 = resolveChallenge(s0, { rm: 1, itemId: 'sticky', isClue: true, correct: false });
    expect(s1.found[1]).not.toContain('sticky');
    expect(s1.turnPos).toBe(1);
  });

  it('decoy tap marks _d_<id>, no score, advances the turn', () => {
    const s0 = freshState();
    const s1 = tapDecoy(s0, 1, 'mug');
    expect(s1.found[1]).toContain('_d_mug');
    expect(s1.rooms[1][ROSTER[0]] ?? 0).toBe(0);
    expect(s1.turnPos).toBe(1);
  });

  it('retapping a tapped decoy is free (no double-advance via tapDecoy)', () => {
    let s = freshState();
    s = tapDecoy(s, 1, 'mug');
    // store-level guard ensures re-tap is free; here we verify the mark doesn't duplicate
    s = tapDecoy(s, 1, 'mug');
    const occurrences = s.found[1].filter((x) => x === '_d_mug').length;
    expect(occurrences).toBe(1);
  });

  it('help: correct → +0.5 to asker and helper, lifeline locked, helper cleared', () => {
    let s = freshState();
    s = setHelper(s, 1, ROSTER[3]);
    s = resolveChallenge(s, { rm: 1, itemId: 'lk1', isClue: false, correct: true });
    expect(s.rooms[1][ROSTER[0]]).toBe(0.5);
    expect(s.rooms[1][ROSTER[3]]).toBe(0.5);
    expect(s.lifelines[1][ROSTER[0]]).toBe(true);
    expect(s.helper[1]).toBeNull();
  });

  it('help: wrong → 0 to both, lifeline still locked, turn still advances', () => {
    let s = freshState();
    s = setHelper(s, 1, ROSTER[3]);
    s = resolveChallenge(s, { rm: 1, itemId: 'lk1', isClue: false, correct: false });
    expect(s.rooms[1][ROSTER[0]] ?? 0).toBe(0);
    expect(s.rooms[1][ROSTER[3]] ?? 0).toBe(0);
    expect(s.lifelines[1][ROSTER[0]]).toBe(true);
    expect(s.turnPos).toBe(1);
  });

  it('cumulative sums across all four rooms', () => {
    const s = freshState();
    addPts(s, 1, ROSTER[0], 2);
    addPts(s, 2, ROSTER[0], 1);
    addPts(s, 4, ROSTER[0], 0.5);
    expect(cumulative(s)[ROSTER[0]]).toBe(3.5);
  });

  it('ranked sorts desc by value, then alpha by name', () => {
    const s = freshState();
    addPts(s, 1, 'Ciara', 3);
    addPts(s, 1, 'Aaron', 3);
    addPts(s, 1, 'Catie', 2);
    const r = ranked(cumulative(s));
    expect(r[0].p).toBe('Aaron');
    expect(r[1].p).toBe('Ciara');
    expect(r[0].rank).toBe(1);
    expect(r[1].rank).toBe(1);
    expect(r.find((x) => x.p === 'Catie')!.rank).toBe(3);
  });
});
