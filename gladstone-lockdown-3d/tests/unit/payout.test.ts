import { describe, it, expect } from 'vitest';
import { ROSTER } from '../../src/data/content';
import { freshState, addPts, payout } from '../../src/game/logic';

describe('Awardco payout', () => {
  it('every player gets at least the 5-point participation bonus', () => {
    const s = freshState();
    addPts(s, 1, 'Ciara', 4);
    addPts(s, 2, 'Catie', 3);
    const arr = payout(s);
    for (const e of arr) {
      expect(e.awardco).toBeGreaterThanOrEqual(5);
    }
  });

  it('podium: 15 / 10 / 7 for ranks 1 / 2 / 3', () => {
    const s = freshState();
    addPts(s, 1, 'Aaron', 10);
    addPts(s, 1, 'Ciara', 7);
    addPts(s, 1, 'Catie', 4);
    addPts(s, 1, 'Jenine', 2);
    const arr = payout(s);
    expect(arr.find((e) => e.player === 'Aaron')!.awardco).toBe(15);
    expect(arr.find((e) => e.player === 'Ciara')!.awardco).toBe(10);
    expect(arr.find((e) => e.player === 'Catie')!.awardco).toBe(7);
    expect(arr.find((e) => e.player === 'Jenine')!.awardco).toBe(5);
  });

  it('ties share rank and the next rank skips by the count of tied players', () => {
    const s = freshState();
    addPts(s, 1, 'Aaron', 5);
    addPts(s, 1, 'Ciara', 5);
    addPts(s, 1, 'Catie', 3);
    const arr = payout(s);
    const aaron = arr.find((e) => e.player === 'Aaron')!;
    const ciara = arr.find((e) => e.player === 'Ciara')!;
    const catie = arr.find((e) => e.player === 'Catie')!;
    expect(aaron.rank).toBe(1);
    expect(ciara.rank).toBe(1);
    expect(catie.rank).toBe(3);
    expect(aaron.bonus).toBe(10);
    expect(ciara.bonus).toBe(10);
    expect(catie.bonus).toBe(2);
  });

  it('returns one entry per roster player', () => {
    const s = freshState();
    expect(payout(s)).toHaveLength(ROSTER.length);
  });
});
