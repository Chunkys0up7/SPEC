import { useState } from 'react';
import { useGame } from '@/game/store';

export default function Header() {
  const route = useGame((s) => s.route);
  const goHub = useGame((s) => s.goHub);
  const goBoard = useGame((s) => s.goBoard);
  const reset = useGame((s) => s.reset);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [howOpen, setHowOpen] = useState(false);

  return (
    <header className="border-b border-white/10">
      <div className="max-w-[1280px] w-full mx-auto px-5 py-4 flex items-center justify-between flex-wrap gap-3">
        <button
          onClick={goHub}
          className="flex items-center gap-3 text-left"
          aria-label="Home"
        >
          <span
            className="w-12 h-12 grid place-items-center rounded-2xl text-2xl"
            style={{
              background: 'rgba(255,255,255,0.06)',
              boxShadow: '0 10px 26px -10px rgba(158,216,99,.6), 0 0 0 2px rgba(158,216,99,.25)',
            }}
          >
            🔒
          </span>
          <span>
            <h1 className="font-display font-black text-[20px] leading-none">Gladstone Lockdown</h1>
            <span className="text-[11.5px] font-semibold tracking-[1.4px] uppercase text-[#b3a9d6]">
              3D Escape Quest · Refresher Friday
            </span>
          </span>
        </button>

        <nav className="flex gap-2 flex-wrap">
          <button onClick={goHub} className={navBtn(route === 'hub')}>
            Home
          </button>
          <button onClick={goBoard} className={navBtn(route === 'board')}>
            Leaderboards
          </button>
          <button onClick={() => setHowOpen(true)} className={navBtn(false)}>
            How to run
          </button>
          <button onClick={() => setConfirmOpen(true)} className={navBtnWarn()}>
            Reset quest
          </button>
        </nav>
      </div>

      {howOpen && <HowToModal onClose={() => setHowOpen(false)} />}
      {confirmOpen && (
        <ConfirmReset
          onClose={() => setConfirmOpen(false)}
          onConfirm={() => {
            reset();
            setConfirmOpen(false);
          }}
        />
      )}
    </header>
  );
}

function navBtn(active: boolean): string {
  return [
    'text-[13px] font-semibold border rounded-[11px] px-4 py-2 transition',
    active
      ? 'border-[#a88bff] text-[#a88bff] bg-[#a88bff]/10'
      : 'border-white/15 text-[#f3eeff] bg-white/5 hover:border-[#a88bff] hover:text-[#a88bff]',
  ].join(' ');
}
function navBtnWarn(): string {
  return 'text-[13px] font-semibold border rounded-[11px] px-4 py-2 transition border-[#ff5a9e]/40 text-[#ff8aa6] hover:bg-[#ff5a9e] hover:text-[#161229] hover:border-[#ff5a9e]';
}

function ConfirmReset({ onClose, onConfirm }: { onClose: () => void; onConfirm: () => void }) {
  return (
    <Modal onClose={onClose}>
      <h3 className="font-display text-[22px] text-[#ff8aa6] mb-2">Reset the whole quest?</h3>
      <p className="text-[14px] text-[#cbc1ed] mb-3">
        This permanently clears every score, lifeline, clue and lock for all 12 players across all
        four rooms. This cannot be undone.
      </p>
      <div className="flex gap-2 flex-wrap mt-4">
        <button
          onClick={onConfirm}
          className="bg-[#f0473f] text-white font-semibold px-5 py-3 rounded-xl"
        >
          Yes, wipe everything
        </button>
        <button onClick={onClose} className="bg-white/10 text-[#f3eeff] font-semibold px-5 py-3 rounded-xl">
          Cancel
        </button>
      </div>
    </Modal>
  );
}

function HowToModal({ onClose }: { onClose: () => void }) {
  return (
    <Modal onClose={onClose}>
      <h3 className="font-display text-[22px] mb-2">How to run Gladstone Lockdown</h3>
      <p className="text-[14px] text-[#cbc1ed] mb-2">
        <b>The setup.</b> Twelve players, four 3D escape rooms. Share your screen and run it from
        here — one room per session, or several in one sitting. No timer.
      </p>
      <ul className="text-[14px] text-[#cbc1ed] list-disc ml-5 space-y-2">
        <li>
          <b>Earn the clues:</b> each room has 6 clues and 6 locks. The on-the-spot player picks an
          object with a dashed outline and answers its question. Correct → they collect the clue
          and score +1. Wrong, or a dead end → no point and the turn passes.
        </li>
        <li>
          <b>Turn rotation:</b> the turn passes automatically after every question (right or
          wrong). Tap any name to jump the turn; <b>Shuffle order</b> to randomise it.
        </li>
        <li>
          <b>Crack a lock:</b> click a glowing 🔒 lock to engage it, hear the answer, then mark{' '}
          <b>Correct ✓</b> or <b>Wrong ✗</b>. <b>Reveal answer</b> shows the key/code.
        </li>
        <li>
          <b>Sealed locks (dim):</b> need a specific clue earned first. The exit needs every other
          lock cracked.
        </li>
        <li>
          <b>Help lifeline:</b> once per asker per room. Correct → both get 0.5. Wrong → both get
          0. The turn still passes.
        </li>
        <li>
          <b>Escape:</b> crack every lock including the exit, then hit <b>Escape Room</b> to bank
          the scores.
        </li>
      </ul>
      <p className="text-[14px] text-[#cbc1ed] mt-3">
        <b>Awardco at the end:</b> everyone who took part gets 5 points. Quest 1st +10, 2nd +5,
        3rd +2 — so 15 / 10 / 7 for the podium.
      </p>
      <p className="text-[13px] text-[#9c91c4] mt-3">
        <b>Keyboard:</b> 1–4 cycle camera presets · R reveal · H help · Y correct · N wrong · S
        shuffle · Esc close overlay.
      </p>
      <p className="text-[13px] text-[#9c91c4] mt-3">
        Scores persist automatically between sessions. “Reset quest” wipes everything.
      </p>
    </Modal>
  );
}

function Modal({ onClose, children }: { onClose: () => void; children: React.ReactNode }) {
  return (
    <div
      className="fixed inset-0 z-50 bg-black/55 grid place-items-center p-6"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-[#1f1b3a] border border-white/10 rounded-2xl p-7 max-w-[560px] w-full relative max-h-[88vh] overflow-auto">
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-3 right-4 w-8 h-8 grid place-items-center rounded-lg bg-white/10 text-[#f3eeff]"
        >
          ✕
        </button>
        {children}
      </div>
    </div>
  );
}
