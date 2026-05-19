import { useGame } from '@/game/store';
import { ROOMS } from '@/data/content';
import { cumulative, fmt, medal, ranked } from '@/game/logic';
import type { Room, RoomId } from '@/game/types';

const ACCENT_VAR: Record<Room['color'], string> = {
  c1: '#9ed863',
  c2: '#46d3ec',
  c3: '#ff5a9e',
  c4: '#a88bff',
};

export default function Hub() {
  const enterRoom = useGame((s) => s.enterRoom);
  const found = useGame((s) => s.found);
  const solved = useGame((s) => s.solved);
  const completed = useGame((s) => s.completed);
  const rooms = useGame((s) => s.rooms);

  const top = ranked(cumulative({ rooms } as any))
    .filter((x) => x.v > 0)
    .slice(0, 5);

  return (
    <div className="pt-6">
      <section className="mb-8">
        <div className="text-[13px] font-bold tracking-[4px] uppercase text-[#ff5a9e]">
          Can your team break out?
        </div>
        <h2 className="font-display font-black leading-[0.9] tracking-tight text-[clamp(40px,8vw,86px)] mt-2">
          <span className="block">GLADSTONE</span>
          <span className="block text-[#46d3ec]">LOCKDOWN</span>
        </h2>
        <div className="font-display font-semibold text-[clamp(15px,2vw,20px)] text-[#b3a9d6] mt-4 flex flex-wrap gap-3 items-center">
          🔍 Find the clues · 🔒 Crack the locks ·{' '}
          <b className="text-[#ffc53d] font-bold">🏁 Escape</b>
        </div>
        <p className="text-[#b3a9d6] text-[15px] max-w-[720px] mt-3">
          Twelve players, four sealed rooms in 3D. Every clue and every lock is a training
          question — the player on the spot answers, scoring +1 for each one they get right. Six
          clues and six locks per room; open every lock to escape. Help lifeline and Awardco
          payout work exactly like Refresher Arena.
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {ROOMS.map((R) => {
          const cracked = R.locks.filter((l) => solved[R.n as RoomId].includes(l.id)).length;
          const clues = R.finds.filter(
            (f) =>
              found[R.n as RoomId].includes(f.id) ||
              found[R.n as RoomId].includes('_d_' + f.id),
          ).length;
          const isDone = completed[R.n as RoomId];
          const inProg = cracked > 0 || clues > 0;
          const status = isDone ? 'done' : inProg ? 'live' : 'todo';
          const statusLabel = isDone ? '✓ Escaped' : inProg ? 'In progress' : 'Locked';
          const accent = ACCENT_VAR[R.color];

          return (
            <button
              key={R.n}
              onClick={() => enterRoom(R.n as RoomId)}
              className="relative text-left rounded-2xl p-6 transition border overflow-hidden hover:-translate-y-1"
              style={{
                background:
                  'linear-gradient(165deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02))',
                borderColor: 'rgba(255,255,255,0.1)',
                boxShadow: `0 22px 40px -26px rgba(0,0,0,0.7)`,
              }}
            >
              <span
                className="absolute left-0 top-0 bottom-0 w-[5px]"
                style={{ background: accent }}
                aria-hidden
              />
              <span className="absolute right-4 top-3 text-[20px]" aria-hidden>
                🔒
              </span>
              <span
                className="absolute right-[-12px] top-[-6px] font-display font-black text-[84px] opacity-[0.12]"
                style={{ color: accent }}
                aria-hidden
              >
                {R.n}
              </span>
              <div className="font-display font-black text-[13px] tracking-[2px]" style={{ color: accent }}>
                ROOM {R.n}
              </div>
              <h3 className="text-[22px] font-bold mt-1 tracking-tight">{R.name}</h3>
              <div
                className="text-[12px] font-semibold uppercase tracking-[1.4px] mt-0.5"
                style={{ color: accent }}
              >
                {R.theme}
              </div>
              <p className="text-[13.5px] text-[#b3a9d6] mt-3 min-h-[52px]">{R.blurb}</p>
              <div className="flex gap-2 items-center flex-wrap mt-3">
                <span className={pillCls(status)}>{statusLabel}</span>
                <span className="text-[12px] text-[#b3a9d6]">
                  Clues {clues}/{R.finds.length} · {cracked}/{R.locks.length} locks
                </span>
              </div>
            </button>
          );
        })}
      </section>

      <section
        className="mt-8 rounded-2xl p-6 border"
        style={{
          background: 'linear-gradient(135deg, rgba(255,197,61,0.12), rgba(255,90,158,0.08))',
          borderColor: 'rgba(255,197,61,0.26)',
        }}
      >
        <h3 className="font-display font-bold text-[19px]">Quest standings — top 5</h3>
        <table className="w-full border-collapse mt-3 text-[14px]">
          <thead>
            <tr>
              <th className="text-left text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Rank
              </th>
              <th className="text-left text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Player
              </th>
              <th className="text-right text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Points
              </th>
            </tr>
          </thead>
          <tbody>
            {top.length === 0 && (
              <tr>
                <td colSpan={3} className="text-[#b3a9d6] py-4 text-[13px]">
                  No points yet — enter a room to begin the quest.
                </td>
              </tr>
            )}
            {top.map((x) => (
              <tr key={x.p}>
                <td className="py-2 border-b border-white/10 font-display font-black w-[54px]">
                  {medal(x.rank)}
                </td>
                <td className="py-2 border-b border-white/10">{x.p}</td>
                <td className="py-2 border-b border-white/10 text-right font-display font-black text-[#ffc53d]">
                  {fmt(x.v)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="text-[13px] text-[#b3a9d6] mt-3">
          Cumulative across all four rooms. Full tables under Leaderboards.
        </p>
      </section>
    </div>
  );
}

function pillCls(status: 'todo' | 'live' | 'done') {
  const base = 'text-[11.5px] font-bold py-1 px-3 rounded-full uppercase tracking-wider';
  if (status === 'done') return base + ' bg-[#ffc53d]/20 text-[#ffc53d]';
  if (status === 'live') return base + ' bg-[#9ed863]/20 text-[#9ed863]';
  return base + ' bg-[#a88bff]/20 text-[#c4b2ff]';
}
