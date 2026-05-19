import { Suspense, useCallback, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import { useGame } from '@/game/store';
import { ROOMS } from '@/data/content';
import type { RoomId } from '@/game/types';
import RoomScene from '@/scene/Room';
import Lighting from '@/scene/Lighting';
import CameraRig, { DEFAULT_EYE, DEFAULT_TGT } from '@/scene/Camera';
import Challenge from './Challenge';
import Dock from './Dock';

export default function RoomView({ rm }: { rm: RoomId }) {
  const R = ROOMS[rm - 1];
  const goHub = useGame((s) => s.goHub);
  const found = useGame((s) => s.found);
  const solved = useGame((s) => s.solved);
  const tap = useGame((s) => s.tap);
  const engagedId = useGame((s) => s.engagedId);
  const closeEngaged = useGame((s) => s.closeEngaged);
  const escape = useGame((s) => s.escape);
  const toggleReveal = useGame((s) => s.toggleReveal);
  const resolveCorrect = useGame((s) => s.resolveCorrect);
  const resolveWrong = useGame((s) => s.resolveWrong);
  const openHelpPicker = useGame((s) => s.openHelpPicker);
  const shuffle = useGame((s) => s.shuffle);

  const [focusEye, setFocusEye] = useState<[number, number, number] | null>(null);
  const [focusTgt, setFocusTgt] = useState<[number, number, number] | null>(null);

  const onObjectFocus = useCallback(
    (eye: [number, number, number] | null, target: [number, number, number] | null) => {
      setFocusEye(eye);
      setFocusTgt(target);
    },
    [],
  );

  useEffect(() => {
    if (!engagedId) {
      setFocusEye(null);
      setFocusTgt(null);
    }
  }, [engagedId]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target && (e.target as HTMLElement).tagName === 'INPUT') return;
      if (e.key === 'Escape') {
        closeEngaged();
        return;
      }
      if (e.key === 'r' || e.key === 'R') toggleReveal();
      if (e.key === 'h' || e.key === 'H') openHelpPicker();
      if (e.key === 'y' || e.key === 'Y') resolveCorrect();
      if (e.key === 'n' || e.key === 'N') resolveWrong();
      if (e.key === 's' || e.key === 'S') shuffle(rm);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [closeEngaged, toggleReveal, openHelpPicker, resolveCorrect, resolveWrong, shuffle, rm]);

  const totalClues = R.finds.length;
  const totalLocks = R.locks.length;
  const cluesFound = R.finds.filter(
    (f) => found[rm].includes(f.id) || found[rm].includes('_d_' + f.id),
  ).length;
  const locksDone = R.locks.filter((l) => solved[rm].includes(l.id)).length;
  const exitLock = R.locks.find((l) => l.exit)!;
  const escaped = solved[rm].includes(exitLock.id);

  const inv = found[rm].filter(
    (id) => !id.startsWith('_d_') && R.finds.some((f) => f.id === id),
  );

  return (
    <div className="pt-2">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-2">
        <div>
          <div className="text-[10.5px] font-bold tracking-[1.4px] uppercase text-[#b3a9d6]">
            Room {rm} · {R.theme} · Clues {cluesFound}/{totalClues} · Locks {locksDone}/
            {totalLocks}
            {escaped ? ' · Escape ready' : ''}
          </div>
          <div className="font-display font-black text-[clamp(20px,2.6vw,26px)] tracking-tight leading-tight mt-0.5">
            {R.name}
          </div>
        </div>
        <button
          onClick={goHub}
          className="text-[13px] font-semibold border border-white/15 bg-white/5 text-[#f3eeff] rounded-[11px] px-4 py-2"
        >
          ← Back to home
        </button>
      </div>

      <div
        className="rounded-2xl overflow-hidden border border-white/10"
        style={{ aspectRatio: '16 / 9', minHeight: 380 }}
      >
        <Canvas
          dpr={[1, 2]}
          shadows
          camera={{ position: DEFAULT_EYE, fov: 50, near: 0.1, far: 80 }}
          gl={{ antialias: true, powerPreference: 'high-performance' }}
        >
          <color attach="background" args={[R.wall]} />
          <fog attach="fog" args={[R.wall, 6, 18]} />
          <Suspense fallback={null}>
            <Lighting accent={R.accent} hasWindow={R.win} />
            <RoomScene
              R={R}
              rm={rm}
              onTap={(id) => tap(rm, id)}
              onObjectFocus={onObjectFocus}
            />
            <CameraRig
              focusEye={focusEye}
              focusTarget={focusTgt}
              enableOrbit={!engagedId}
            />
            <EffectComposer>
              <Bloom mipmapBlur intensity={0.45} luminanceThreshold={0.6} />
              <Vignette eskil={false} offset={0.18} darkness={0.85} />
            </EffectComposer>
          </Suspense>
        </Canvas>
      </div>

      {/* clue inventory */}
      <div
        className="mt-3 rounded-xl px-4 py-2.5 border"
        style={{ background: 'rgba(255,255,255,0.04)', borderColor: 'rgba(255,255,255,0.1)' }}
      >
        <div className="text-[10.5px] font-bold tracking-[1.3px] uppercase text-[#b3a9d6] mb-1.5">
          Clue inventory
        </div>
        <div className="flex flex-wrap gap-2">
          {inv.length === 0 ? (
            <span className="text-[13px] text-[#b3a9d6]">
              No clues collected yet — click around the room to search.
            </span>
          ) : (
            inv.map((id) => {
              const f = R.finds.find((x) => x.id === id)!;
              return (
                <span
                  key={id}
                  className="text-[13px] font-semibold border border-white/15 bg-white/5 text-[#f3eeff] px-3 py-1.5 rounded-full"
                  title={f.text}
                >
                  🔎 {f.label}
                </span>
              );
            })
          )}
        </div>
      </div>

      <Challenge rm={rm} />

      {escaped && (
        <div className="text-center mt-4">
          <button
            onClick={() => escape(rm)}
            className="font-display font-black text-[20px] text-white px-10 py-4 rounded-2xl"
            style={{
              background: 'linear-gradient(135deg, #19b36b, #0f8f55)',
              boxShadow: '0 16px 34px -14px rgba(25,179,107,.7)',
            }}
          >
            🏁 Escape Room {rm}
          </button>
          <p className="text-[13px] text-[#b3a9d6] mt-2">
            All locks cracked. Lock in the room to bank the scores.
          </p>
        </div>
      )}

      <Dock rm={rm} />

      {/* a11y: hidden list of every interactive object for keyboard nav */}
      <KeyboardObjectList rm={rm} />
    </div>
  );
}

function KeyboardObjectList({ rm }: { rm: RoomId }) {
  const R = ROOMS[rm - 1];
  const tap = useGame((s) => s.tap);
  const found = useGame((s) => s.found);
  const solved = useGame((s) => s.solved);
  return (
    <details className="mt-3 text-[13px] text-[#b3a9d6]">
      <summary className="cursor-pointer">Keyboard / a11y: list interactable objects</summary>
      <ul className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-1.5">
        {[...R.finds, ...R.locks].map((o) => {
          const isClue = R.finds.includes(o as any);
          const id = (o as any).id as string;
          const label = isClue ? (o as any).label : (o as any).title;
          const isFoundOrSolved = isClue
            ? found[rm].includes(id) || found[rm].includes('_d_' + id)
            : solved[rm].includes(id);
          return (
            <li key={id}>
              <button
                className="underline hover:text-[#f3eeff]"
                onClick={() => tap(rm, id)}
                aria-label={`${label} ${isFoundOrSolved ? 'done' : 'open'}`}
              >
                {label}
                {isFoundOrSolved ? ' ✓' : ''}
              </button>
            </li>
          );
        })}
      </ul>
    </details>
  );
}
