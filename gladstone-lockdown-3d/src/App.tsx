import { useEffect } from 'react';
import { useGame } from '@/game/store';
import Hub from '@/ui/Hub';
import RoomView from '@/ui/RoomView';
import Leaderboards from '@/ui/Leaderboards';
import Header from '@/ui/Header';
import HowTo from '@/ui/HowTo';
import Toast from '@/ui/Toast';

export default function App() {
  const route = useGame((s) => s.route);
  const currentRoom = useGame((s) => s.currentRoom);
  const toast = useGame((s) => s.toast);
  const setToast = useGame((s) => s.setToast);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(t);
  }, [toast, setToast]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-[1280px] w-full mx-auto px-5 pb-12 pt-2">
        {route === 'hub' && <Hub />}
        {route === 'room' && currentRoom != null && <RoomView rm={currentRoom} />}
        {route === 'board' && <Leaderboards />}
        {route === 'howto' && <HowTo />}
      </main>
      <footer className="text-center text-[12.5px] text-[#b3a9d6] py-6">
        Gladstone Lockdown · 3D Refresher Friday · Built on the same engine as Refresher Arena.
      </footer>
      <Toast />
    </div>
  );
}
