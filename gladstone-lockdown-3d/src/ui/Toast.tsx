import { useGame } from '@/game/store';

export default function Toast() {
  const toast = useGame((s) => s.toast);
  return (
    <div
      className={[
        'fixed left-1/2 -translate-x-1/2 bottom-8 px-6 py-3 rounded-xl text-[14px] font-semibold z-[60]',
        'bg-[#231f4a] text-white max-w-[520px] text-center pointer-events-none transition-opacity duration-200',
        toast ? 'opacity-100' : 'opacity-0',
      ].join(' ')}
      role="status"
      aria-live="polite"
    >
      {toast ?? ''}
    </div>
  );
}
