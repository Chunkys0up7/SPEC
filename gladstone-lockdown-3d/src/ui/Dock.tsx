import { useGame } from '@/game/store';
import type { RoomId } from '@/game/types';
import { ROSTER } from '@/data/content';
import { curP, nextP, roomTotals, ranked, fmt } from '@/game/logic';
import { useState } from 'react';

interface Props {
  rm: RoomId;
}

export default function Dock({ rm }: Props) {
  const order = useGame((s) => s.order);
  const turnPos = useGame((s) => s.turnPos);
  const helper = useGame((s) => s.helper);
  const lifelines = useGame((s) => s.lifelines);
  const rooms = useGame((s) => s.rooms);
  const engagedId = useGame((s) => s.engagedId);
  const pick = useGame((s) => s.pick);
  const shuffle = useGame((s) => s.shuffle);
  const openHelp = useGame((s) => s.openHelpPicker);
  const helperPickerOpen = useGame((s) => s.helperPickerOpen);
  const closeHelp = useGame((s) => s.closeHelpPicker);
  const setHelper = useGame((s) => s.setHelper);
  const toggleReveal = useGame((s) => s.toggleReveal);
  const resolveCorrect = useGame((s) => s.resolveCorrect);
  const resolveWrong = useGame((s) => s.resolveWrong);

  const s = { order, turnPos } as any;
  const act = curP(s);
  const up = nextP(s);
  const tot = roomTotals({ rooms } as any, rm);
  const mini = ranked(tot)
    .filter((x) => x.v > 0)
    .slice(0, 6);

  const canScore = engagedId != null;
  const helping = helper[rm] !== null && helper[rm] !== undefined;
  const lifeUsed = (p: string) => !!lifelines[rm][p];
  const canHelp = canScore && !helping && !lifeUsed(act);

  return (
    <div
      className="sticky bottom-0 z-10 mt-3 rounded-t-2xl p-4 border"
      style={{
        background: 'rgba(20, 17, 40, 0.95)',
        borderColor: 'rgba(255,255,255,0.1)',
        boxShadow: '0 -16px 30px -22px rgba(0,0,0,0.7)',
      }}
    >
      {/* turn bar */}
      <div className="flex items-end flex-wrap gap-4 pb-2 border-b border-white/10">
        <div>
          <div className="text-[9.5px] font-bold tracking-[1.2px] uppercase text-[#b3a9d6]">
            On the spot · turn {turnPos + 1}
          </div>
          <div className="font-display font-black text-[20px] text-[#a88bff] leading-none mt-0.5">
            {act}
          </div>
        </div>
        <div className="pl-4 border-l border-white/10">
          <div className="text-[9.5px] font-bold tracking-[1.2px] uppercase text-[#b3a9d6]">
            Up next
          </div>
          <div className="font-display font-bold text-[14px] text-[#cbc1ed] mt-0.5">{up}</div>
        </div>
        <button
          onClick={() => shuffle(rm)}
          className="ml-auto bg-white/10 text-[#f3eeff] text-[12px] font-bold px-3 py-2 rounded-lg"
          aria-label="Shuffle turn order"
        >
          🔀 Shuffle order
        </button>
      </div>

      {/* chip row */}
      <div className="mt-3">
        <div className="text-[9.5px] font-bold tracking-[1.2px] uppercase text-[#b3a9d6]">
          Turn order — tap a name to jump the turn (absences/skips)
        </div>
        <div className="flex flex-wrap gap-1.5 mt-1.5 max-w-[820px]">
          {order.map((p, i) => {
            const isActive = p === act;
            const isHelper = p === helper[rm];
            const turned = i < turnPos % order.length;
            return (
              <button
                key={p}
                onClick={() => pick(rm, p)}
                title={`Jump the turn to ${p}`}
                className={[
                  'text-[11.5px] font-semibold border rounded-lg px-2.5 py-1',
                  isActive
                    ? 'bg-[#5b5bd6] text-white border-[#5b5bd6]'
                    : isHelper
                      ? 'bg-[#ffc53d] text-[#5a3d00] border-[#ffc53d]'
                      : 'bg-white/5 text-[#f3eeff] border-white/15',
                  turned && !isActive && !isHelper ? 'opacity-40 line-through' : '',
                ].join(' ')}
              >
                {p}
                {lifeUsed(p) && p === act ? ' ·🔒' : ''}
              </button>
            );
          })}
        </div>
      </div>

      {/* action row */}
      <div className="flex justify-between gap-3 flex-wrap items-end mt-3">
        <div className="flex gap-2 flex-wrap">
          <button
            disabled={!canScore}
            onClick={toggleReveal}
            className={btnCls('rev', !canScore)}
          >
            Reveal answer
          </button>
          <button
            disabled={!canHelp}
            onClick={openHelp}
            className={btnCls('help', !canHelp)}
          >
            Use help · {lifeUsed(act) ? 'used' : 'available'}
          </button>
          <button
            disabled={!canScore}
            onClick={resolveCorrect}
            className={btnCls('good', !canScore)}
          >
            Correct ✓
          </button>
          <button
            disabled={!canScore}
            onClick={resolveWrong}
            className={btnCls('bad', !canScore)}
          >
            Wrong ✗
          </button>
        </div>
        <div className="flex gap-3 flex-wrap text-[12px] text-[#cbc1ed]">
          {mini.length === 0 ? (
            <span className="text-[#b3a9d6]">No points scored in this room yet.</span>
          ) : (
            mini.map((x) => (
              <span key={x.p}>
                {x.p} <b className="font-display text-[#ffc53d]">{fmt(x.v)}</b>
              </span>
            ))
          )}
        </div>
      </div>

      {helping && (
        <div
          className="mt-2 text-[12px] rounded-lg px-3 py-2 border"
          style={{
            background: 'rgba(255,197,61,0.1)',
            borderColor: 'rgba(255,197,61,0.4)',
            color: '#ffd76a',
          }}
        >
          💡 Help in play: <b>{act}</b> nominated <b>{helper[rm]}</b>. Correct → both get 0.5 ·
          Wrong → both get 0. The turn still passes on after.
        </div>
      )}

      {!engagedId && (
        <div className="mt-2 text-[12px] rounded-lg px-3 py-2 border border-white/10 bg-white/5 text-[#cbc1ed]">
          Click a glowing 🔒 lock in the room to engage it — then {act} answers.
        </div>
      )}

      {helperPickerOpen && (
        <HelperPicker
          act={act}
          onClose={closeHelp}
          onPick={(p) => setHelper(rm, p)}
        />
      )}
    </div>
  );
}

function btnCls(kind: 'rev' | 'help' | 'good' | 'bad', disabled: boolean) {
  const base = 'text-[12px] font-bold rounded-lg px-3.5 py-2 transition';
  const dis = disabled ? ' opacity-40 cursor-not-allowed' : '';
  if (kind === 'good') return base + ' bg-[#19b36b] text-white' + dis;
  if (kind === 'bad') return base + ' bg-[#f0473f] text-white' + dis;
  if (kind === 'help') return base + ' bg-[#ffc53d] text-[#5a3d00]' + dis;
  return base + ' bg-white/10 text-[#f3eeff]' + dis;
}

function HelperPicker({
  act,
  onClose,
  onPick,
}: {
  act: string;
  onClose: () => void;
  onPick: (p: string) => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 bg-black/55 grid place-items-center p-6"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-[#1f1b3a] border border-white/10 rounded-2xl p-6 max-w-[560px] w-full">
        <button
          onClick={onClose}
          className="float-right w-8 h-8 grid place-items-center rounded-lg bg-white/10"
          aria-label="Close"
        >
          ✕
        </button>
        <h3 className="font-display text-[22px]">{act} calls for help</h3>
        <p className="text-[14px] text-[#cbc1ed] mt-2">
          Nominate one teammate to help crack this lock. If the answer is right,{' '}
          <b>both get 0.5 points</b>. If it's wrong, both get 0. {act} can only use help once in
          this room, and the turn still passes on after.
        </p>
        <div className="flex flex-wrap gap-2 mt-3">
          {ROSTER.filter((p) => p !== act).map((p) => (
            <button
              key={p}
              onClick={() => onPick(p)}
              className="bg-white/5 border border-white/15 px-3 py-1.5 rounded-lg text-[13px]"
            >
              {p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// keep `useState` referenced to avoid unused-import warning if compiler is strict
void useState;
