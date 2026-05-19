import { useGame } from '@/game/store';

export default function HowTo() {
  const goHub = useGame((s) => s.goHub);
  return (
    <div className="max-w-[760px] mx-auto py-6">
      <h2 className="font-display text-3xl mb-4">How to run Gladstone Lockdown</h2>
      <p className="text-[#cbc1ed] text-[15px]">See the “How to run” modal in the header.</p>
      <button onClick={goHub} className="mt-6 bg-white/10 px-4 py-2 rounded-xl">
        ← Back to home
      </button>
    </div>
  );
}
