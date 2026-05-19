import { useState } from 'react';
import { useGame } from '@/game/store';
import { ROOMS } from '@/data/content';
import type { RoomId } from '@/game/types';
import { cumulative, fmt, medal, payout, ranked, roomTotals } from '@/game/logic';

type Tab = 'r1' | 'r2' | 'r3' | 'r4' | 'cum' | 'pay';

export default function Leaderboards() {
  const [tab, setTab] = useState<Tab>('cum');
  const state = useGame();
  const completed = state.completed;

  return (
    <div className="pt-4">
      <div className="text-[13px] font-bold tracking-[4px] uppercase text-[#ff5a9e]">Standings</div>
      <h2 className="font-display font-black text-[clamp(28px,4vw,42px)]">Leaderboards</h2>

      <div className="flex flex-wrap gap-2 mt-4">
        {(['r1', 'r2', 'r3', 'r4', 'cum', 'pay'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={[
              'text-[13px] font-semibold border rounded-[10px] px-3.5 py-2',
              tab === t
                ? 'bg-[#5b5bd6] text-white border-[#5b5bd6]'
                : 'bg-white/5 text-[#cbc1ed] border-white/15',
            ].join(' ')}
          >
            {t === 'cum' ? 'Quest total' : t === 'pay' ? 'Awardco payout' : `Room ${t.slice(1)}`}
          </button>
        ))}
      </div>

      <div className="mt-5">
        {tab === 'pay' ? (
          <Payout state={state} />
        ) : tab === 'cum' ? (
          <RankTable
            head={'Quest total · all four rooms'}
            rows={ranked(cumulative(state)).map((x) => ({ p: x.p, v: x.v, rank: x.rank }))}
          />
        ) : (
          <RankTable
            head={`${ROOMS[parseInt(tab.slice(1)) - 1].name} · Room ${tab.slice(1)}`}
            rows={ranked(roomTotals(state, parseInt(tab.slice(1)) as RoomId)).map((x) => ({
              p: x.p,
              v: x.v,
              rank: x.rank,
            }))}
            empty={
              !completed[parseInt(tab.slice(1)) as RoomId] &&
              ranked(roomTotals(state, parseInt(tab.slice(1)) as RoomId)).every((x) => x.v === 0)
                ? 'This room has not been played yet.'
                : undefined
            }
          />
        )}
      </div>
    </div>
  );
}

function RankTable({
  head,
  rows,
  empty,
}: {
  head: string;
  rows: { p: string; v: number; rank: number }[];
  empty?: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
      <h3 className="font-display text-[19px] text-[#ffc53d] mb-2">{head}</h3>
      {empty && <p className="text-[13px] text-[#b3a9d6] py-2">{empty}</p>}
      <table className="w-full border-collapse mt-2 text-[14px]">
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
          {rows.map((x) => (
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
    </div>
  );
}

function Payout({ state }: { state: any }) {
  const arr = payout(state);
  const get = (r: number) => arr.filter((x) => x.rank === r).map((x) => x.player);
  const p1 = get(1);
  const p2 = get(2);
  const p3 = get(3);
  const allDone = ([1, 2, 3, 4] as RoomId[]).every((w) => state.completed[w]);
  const tie = p1.length > 1 || p2.length > 1 || p3.length > 1;

  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <h3 className="font-display text-[19px] text-[#ffc53d] mb-2">
          End-of-quest Awardco payout
        </h3>
        <p className="text-[13px] text-[#b3a9d6] mb-3">
          {allDone
            ? 'All four rooms escaped — final standings below.'
            : 'Provisional — based on rooms completed so far. Finalises when Room 4 is escaped.'}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { label: '1st place', names: p1, award: '15', gold: true },
            { label: '2nd place', names: p2, award: '10', gold: false },
            { label: '3rd place', names: p3, award: '7', gold: false },
          ].map((c) => (
            <div
              key={c.label}
              className="rounded-xl p-4 text-center border"
              style={{
                background: c.gold ? 'rgba(255,197,61,0.1)' : 'rgba(255,255,255,0.04)',
                borderColor: c.gold ? '#ffc53d' : 'rgba(255,255,255,0.1)',
              }}
            >
              <div className="text-[12px] font-bold uppercase tracking-[1.5px] text-[#b3a9d6]">
                {c.label}
              </div>
              <div className="font-display font-bold text-[19px] my-2">
                {c.names.length ? c.names.join(' & ') : '—'}
              </div>
              <div className="text-[13px] text-[#cbc1ed]">
                <b className="font-display text-[21px] text-[#ffc53d]">{c.award}</b> Awardco pts
                <br />
                <span className="text-[#b3a9d6]">incl. 5 participation</span>
              </div>
            </div>
          ))}
        </div>
        {tie && (
          <p className="text-[13px] text-[#b3a9d6] mt-3">
            A tie shares a rank — confirm the split with the team or use Room 4 as the tie-breaker
            before paying out.
          </p>
        )}
        <div className="mt-5 border-t border-dashed border-white/15 pt-3">
          <p className="text-[13.5px]">
            <b>Every participating team member</b> receives <b>5 Awardco points</b> for taking
            part. On top of participation: <b>1st +10</b>, <b>2nd +5</b>, <b>3rd +2</b>.
          </p>
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <h3 className="font-display text-[19px] text-[#ffc53d] mb-2">Full quest table</h3>
        <table className="w-full border-collapse mt-2 text-[14px]">
          <thead>
            <tr>
              <th className="text-left text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Rank
              </th>
              <th className="text-left text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Player
              </th>
              <th className="text-left text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Quest pts
              </th>
              <th className="text-right text-[11.5px] uppercase tracking-[1px] text-[#b3a9d6] py-2 border-b border-white/15">
                Awardco
              </th>
            </tr>
          </thead>
          <tbody>
            {arr.map((x) => (
              <tr key={x.player}>
                <td className="py-2 border-b border-white/10 font-display font-black w-[54px]">
                  {medal(x.rank)}
                </td>
                <td className="py-2 border-b border-white/10">{x.player}</td>
                <td className="py-2 border-b border-white/10">{fmt(x.questPts)}</td>
                <td className="py-2 border-b border-white/10 text-right font-display font-black text-[#ffc53d]">
                  {x.awardco}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
