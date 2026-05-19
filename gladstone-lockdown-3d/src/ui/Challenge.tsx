import { useGame } from '@/game/store';
import type { Find, Lock, RoomId } from '@/game/types';
import { ROOMS } from '@/data/content';

interface Props {
  rm: RoomId;
}

export default function Challenge({ rm }: Props) {
  const engagedId = useGame((s) => s.engagedId);
  const reveal = useGame((s) => s.reveal);
  const solved = useGame((s) => s.solved);

  if (!engagedId) return null;
  const R = ROOMS[rm - 1];
  const lock: Lock | undefined = R.locks.find((l) => l.id === engagedId);
  const find: Find | undefined = R.finds.find((f) => f.id === engagedId && !f.decoy);
  const L = lock ?? find;
  if (!L) return null;
  const isClue = !!find && !lock;
  const exitLock = R.locks.find((l) => l.exit)!;
  const escaped = solved[rm].includes(exitLock.id);

  const head = isClue
    ? `Clue challenge · ${(L as Find).label}`
    : `${escaped ? 'Locked door' : 'Lock engaged'} · ${(L as Lock).title}`;

  return (
    <div
      className="rounded-2xl p-6 mt-4 border border-l-[6px]"
      style={{
        background: 'rgba(31, 27, 58, 0.75)',
        borderColor: 'rgba(255,255,255,0.08)',
        borderLeftColor: '#a88bff',
      }}
    >
      <div className="text-[12px] font-bold tracking-[2px] uppercase text-[#b3a9d6]">{head}</div>
      <div className="font-display font-bold text-[clamp(20px,2.6vw,26px)] my-3 leading-tight">
        {L.q}
      </div>
      {L.kind === 'code' ? (
        <CodeBox code={L.code!} reveal={reveal} />
      ) : (
        <Options options={L.o!} correctIndex={L.a!} reveal={reveal} />
      )}
      <p className="text-[13px] text-[#b3a9d6] mt-4">
        The player on the spot answers, then mark it.{' '}
        {isClue
          ? 'Correct → they earn the clue and +1. Wrong → no clue, turn passes.'
          : L.kind === 'code'
            ? 'Use “Reveal answer” to show the code.'
            : 'Use “Reveal answer” to show the key.'}
      </p>
    </div>
  );
}

function Options({
  options,
  correctIndex,
  reveal,
}: {
  options: [string, string, string, string];
  correctIndex: number;
  reveal: boolean;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {options.map((o, i) => {
        const right = reveal && i === correctIndex;
        return (
          <div
            key={i}
            className={[
              'rounded-xl px-4 py-3 flex items-center gap-3 text-[15px] font-semibold border',
              right
                ? 'bg-[#19b36b]/15 border-[#19b36b]'
                : 'bg-white/5 border-white/10 text-[#f3eeff]',
            ].join(' ')}
          >
            <span
              className={[
                'w-7 h-7 rounded-lg grid place-items-center font-display font-black text-[14px] flex-none',
                right ? 'bg-[#19b36b] text-white' : 'bg-white/10 text-[#cbc1ed]',
              ].join(' ')}
            >
              {'ABCD'[i]}
            </span>
            <span>{o}</span>
          </div>
        );
      })}
    </div>
  );
}

function CodeBox({ code, reveal }: { code: string; reveal: boolean }) {
  return (
    <div className="text-center py-2">
      <div className="text-[13px] text-[#b3a9d6] font-semibold">
        Code lock — the player enters the code aloud
      </div>
      <div
        className={[
          'font-display font-black mt-2',
          reveal ? 'text-[#ffc53d] text-[40px] tracking-[4px]' : 'text-[#b3a9d6] text-[40px] tracking-[8px]',
        ].join(' ')}
      >
        {reveal ? code : '• • • • •'}
      </div>
    </div>
  );
}
