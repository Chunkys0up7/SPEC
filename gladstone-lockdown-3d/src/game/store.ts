import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { ROOMS } from '@/data/content';
import {
  freshState,
  resolveChallenge,
  tapDecoy,
  pickPlayer,
  shuffleOrder,
  setHelper as setHelperPure,
  finishRoom,
  migrate,
} from './logic';
import type { GameState, RoomId } from './types';

interface Transient {
  route: 'hub' | 'room' | 'board' | 'howto';
  currentRoom: RoomId | null;
  engagedId: string | null; // lock or clue id being challenged
  reveal: boolean;
  helperPickerOpen: boolean;
  toast: string | null;
}

interface Actions {
  // navigation
  goHub: () => void;
  enterRoom: (rm: RoomId) => void;
  goBoard: () => void;

  // engagement
  tap: (rm: RoomId, id: string) => { ok: boolean; reason?: string };
  closeEngaged: () => void;
  toggleReveal: () => void;

  // resolve / scoring
  resolveCorrect: () => void;
  resolveWrong: () => void;

  // rotation
  pick: (rm: RoomId, p: string) => void;
  shuffle: (rm: RoomId) => void;

  // help
  openHelpPicker: () => void;
  closeHelpPicker: () => void;
  setHelper: (rm: RoomId, p: string) => void;

  // escape / reset
  escape: (rm: RoomId) => void;
  reset: () => void;

  // toast
  setToast: (msg: string | null) => void;
}

export interface GameStore extends GameState, Transient, Actions {}

export const PERSIST_KEY = 'gladstone_lockdown_3d_v1';

export const useGame = create<GameStore>()(
  persist(
    (set, get) => ({
      ...freshState(),
      route: 'hub',
      currentRoom: null,
      engagedId: null,
      reveal: false,
      helperPickerOpen: false,
      toast: null,

      goHub: () => set({ route: 'hub', currentRoom: null, engagedId: null, reveal: false }),
      enterRoom: (rm) =>
        set({ route: 'room', currentRoom: rm, engagedId: null, reveal: false }),
      goBoard: () => set({ route: 'board' }),

      tap: (rm, id) => {
        const s = get();
        const R = ROOMS[rm - 1];
        const find = R.finds.find((f) => f.id === id);
        if (find) {
          const already =
            s.found[rm].includes(id) || s.found[rm].includes('_d_' + id);
          if (already) {
            return { ok: true };
          }
          if (find.decoy) {
            const next = tapDecoy(s, rm, id);
            set({ ...next, toast: find.text + '  —  Turn passes.' });
            return { ok: true };
          }
          set({ engagedId: id, reveal: false });
          return { ok: true };
        }
        const lock = R.locks.find((l) => l.id === id);
        if (!lock) return { ok: false };
        if (s.solved[rm].includes(id)) {
          set({ toast: 'That lock is already cracked.' });
          return { ok: false, reason: 'open' };
        }
        const reqMet = !lock.requires || s.found[rm].includes(lock.requires);
        if (lock.exit) {
          const allOther = R.locks.filter((l) => !l.exit).every((l) => s.solved[rm].includes(l.id));
          if (!allOther || !reqMet) {
            set({ toast: 'The exit is sealed — crack every other lock first.' });
            return { ok: false, reason: 'sealed' };
          }
        } else if (!reqMet) {
          set({ toast: 'It won’t budge yet — you need a clue first.' });
          return { ok: false, reason: 'sealed' };
        }
        set({ engagedId: id, reveal: false });
        return { ok: true };
      },

      closeEngaged: () => set({ engagedId: null, reveal: false }),
      toggleReveal: () => set((s) => ({ reveal: !s.reveal })),

      resolveCorrect: () => {
        const s = get();
        if (!s.engagedId || s.currentRoom == null) return;
        const rm = s.currentRoom;
        const R = ROOMS[rm - 1];
        const lock = R.locks.find((l) => l.id === s.engagedId);
        const find = R.finds.find((f) => f.id === s.engagedId && !f.decoy);
        const isClue = !!find && !lock;
        const next = resolveChallenge(s, {
          rm,
          itemId: s.engagedId,
          isClue,
          correct: true,
        });
        set({ ...next, engagedId: null, reveal: false });
      },
      resolveWrong: () => {
        const s = get();
        if (!s.engagedId || s.currentRoom == null) return;
        const rm = s.currentRoom;
        const R = ROOMS[rm - 1];
        const lock = R.locks.find((l) => l.id === s.engagedId);
        const find = R.finds.find((f) => f.id === s.engagedId && !f.decoy);
        const isClue = !!find && !lock;
        const next = resolveChallenge(s, {
          rm,
          itemId: s.engagedId,
          isClue,
          correct: false,
        });
        set({ ...next, engagedId: null, reveal: false });
      },

      pick: (rm, p) => set((s) => ({ ...pickPlayer(s, rm, p) })),
      shuffle: (rm) =>
        set((s) => ({
          ...shuffleOrder(s, rm),
          toast: 'Turn order shuffled.',
        })),

      openHelpPicker: () => set({ helperPickerOpen: true }),
      closeHelpPicker: () => set({ helperPickerOpen: false }),
      setHelper: (rm, p) =>
        set((s) => ({ ...setHelperPure(s, rm, p), helperPickerOpen: false })),

      escape: (rm) => {
        const s = get();
        const next = finishRoom(s, rm);
        set({
          ...next,
          route: 'board',
          currentRoom: null,
          engagedId: null,
          toast: `Room ${rm} escaped — scores banked`,
        });
      },

      reset: () => {
        const fresh = freshState();
        set({
          ...fresh,
          route: 'hub',
          currentRoom: null,
          engagedId: null,
          reveal: false,
          helperPickerOpen: false,
          toast: null,
        });
      },

      setToast: (msg) => set({ toast: msg }),
    }),
    {
      name: PERSIST_KEY,
      version: 3,
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({
        v: s.v,
        order: s.order,
        turnPos: s.turnPos,
        found: s.found,
        solved: s.solved,
        rooms: s.rooms,
        lifelines: s.lifelines,
        helper: s.helper,
        completed: s.completed,
      }),
      migrate: (persisted: any) => migrate(persisted),
    },
  ),
);
