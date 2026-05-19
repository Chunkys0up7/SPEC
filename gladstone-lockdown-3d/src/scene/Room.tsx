import { useMemo } from 'react';
import { useSpring, animated } from '@react-spring/three';
import { Html } from '@react-three/drei';
import type { Room, RoomId, SpotState } from '@/game/types';
import { useGame } from '@/game/store';
import { spotState } from '@/game/logic';
import { ROOMS } from '@/data/content';
import { Furniture, isWallMounted, getSpec } from './Furniture';

const ROOM_W = 6;
const ROOM_D = 5;
const ROOM_H = 3;

const PRM =
  typeof window !== 'undefined' && window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

export interface PlacedObject {
  id: string;
  type: 'find' | 'lock';
  position: [number, number, number];
  rotation: [number, number, number];
  art: import('@/game/types').ArtType;
  isExit: boolean;
  label: string;
  state: SpotState;
}

export function placeObjects(rm: RoomId, state: any): PlacedObject[] {
  const R = ROOMS[rm - 1];
  const all = [
    ...R.finds.map((f) => ({ ...f, type: 'find' as const })),
    ...R.locks.map((l) => ({ ...l, type: 'lock' as const })),
  ];
  const exitObj = all.find((o) => 'exit' in o && o.exit);
  const wallItems = all.filter((o) => !('exit' in o && o.exit) && isWallMounted(o.art));
  const floorItems = all.filter((o) => !('exit' in o && o.exit) && !isWallMounted(o.art));

  const placed: PlacedObject[] = [];

  // Wall items on the back wall (z = -ROOM_D/2 + small offset)
  const wallX = (n: number, i: number, lo = -ROOM_W / 2 + 0.9, hi = ROOM_W / 2 - 0.9) => {
    if (n <= 1) return (lo + hi) / 2;
    return lo + (i * (hi - lo)) / (n - 1);
  };
  const winOffset = R.win ? 0.6 : 0; // shift wall items right to clear window
  if (wallItems.length <= 3) {
    wallItems.forEach((o, i) => {
      const x = wallX(wallItems.length, i, -ROOM_W / 2 + 0.9 + winOffset);
      placed.push(make(rm, state, o, [x, 1.85, -ROOM_D / 2 + 0.06], [0, 0, 0]));
    });
  } else {
    const rowA = wallItems.filter((_, i) => i % 2 === 0);
    const rowB = wallItems.filter((_, i) => i % 2 === 1);
    rowA.forEach((o, i) => {
      const x = wallX(rowA.length, i, -ROOM_W / 2 + 0.9 + winOffset);
      placed.push(make(rm, state, o, [x, 2.15, -ROOM_D / 2 + 0.06], [0, 0, 0]));
    });
    rowB.forEach((o, i) => {
      const lo = -ROOM_W / 2 + 1.4 + winOffset;
      const hi = ROOM_W / 2 - 1.4;
      const x = rowB.length <= 1 ? (lo + hi) / 2 : lo + (i * (hi - lo)) / (rowB.length - 1);
      placed.push(make(rm, state, o, [x, 1.3, -ROOM_D / 2 + 0.06], [0, 0, 0]));
    });
  }

  // Floor items in two staggered rows, exit pinned far right
  const flo = -ROOM_W / 2 + 0.9;
  const fhi = exitObj ? ROOM_W / 2 - 1.7 : ROOM_W / 2 - 0.9;
  const n = floorItems.length;
  floorItems.forEach((o, i) => {
    const t = n <= 1 ? 0.5 : i / (n - 1);
    const x = flo + t * (fhi - flo);
    const z = i % 2 === 0 ? -ROOM_D / 2 + 1.4 : -ROOM_D / 2 + 2.3;
    const spec = getSpec(o.art);
    const y = spec.size[1] / 2;
    placed.push(make(rm, state, o, [x, y, z], [0, 0, 0]));
  });

  if (exitObj) {
    const spec = getSpec(exitObj.art);
    placed.push(
      make(rm, state, exitObj, [ROOM_W / 2 - 0.9, spec.size[1] / 2, 0], [0, -Math.PI / 2, 0]),
    );
  }

  return placed;
}

function make(
  rm: RoomId,
  state: any,
  obj: any,
  position: [number, number, number],
  rotation: [number, number, number],
): PlacedObject {
  const st = spotState(state, rm, obj as any);
  return {
    id: obj.id,
    type: obj.type,
    position,
    rotation,
    art: obj.art,
    isExit: !!obj.exit,
    label: obj.label ?? obj.title ?? '',
    state: st,
  };
}

export default function RoomScene({
  R,
  rm,
  onTap,
  onObjectFocus,
}: {
  R: Room;
  rm: RoomId;
  onTap: (id: string) => void;
  onObjectFocus: (eye: [number, number, number] | null, target: [number, number, number] | null) => void;
}) {
  const state = useGame();
  const placed = useMemo(() => placeObjects(rm, state), [rm, state]);
  const exitSolved = state.solved[rm].includes('exit');

  // door swing for exit if solved
  const doorSwing = useSpring({
    rotY: exitSolved ? (95 * Math.PI) / 180 : 0,
    immediate: PRM,
    config: { mass: 1, tension: 80, friction: 22 },
  });

  return (
    <group>
      {/* floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[ROOM_W, ROOM_D]} />
        <meshStandardMaterial color={R.floor} roughness={0.9} />
      </mesh>
      {/* back wall */}
      <mesh position={[0, ROOM_H / 2, -ROOM_D / 2]} receiveShadow>
        <planeGeometry args={[ROOM_W, ROOM_H]} />
        <meshStandardMaterial color={R.wall} roughness={0.95} />
      </mesh>
      {/* left wall */}
      <mesh position={[-ROOM_W / 2, ROOM_H / 2, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[ROOM_D, ROOM_H]} />
        <meshStandardMaterial color={R.wall} roughness={0.95} />
      </mesh>
      {/* right wall */}
      <mesh position={[ROOM_W / 2, ROOM_H / 2, 0]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[ROOM_D, ROOM_H]} />
        <meshStandardMaterial color={R.wall} roughness={0.95} />
      </mesh>
      {/* ceiling */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, ROOM_H, 0]}>
        <planeGeometry args={[ROOM_W, ROOM_D]} />
        <meshStandardMaterial color="#1a1530" roughness={1} />
      </mesh>
      {/* baseboard */}
      <mesh position={[0, 0.08, -ROOM_D / 2 + 0.03]}>
        <boxGeometry args={[ROOM_W, 0.16, 0.04]} />
        <meshStandardMaterial color="#0e0a1a" />
      </mesh>

      {/* window for rooms 1 + 3 */}
      {R.win && (
        <group position={[-ROOM_W / 2 + 0.04, 1.7, -1.5]}>
          <mesh rotation={[0, Math.PI / 2, 0]}>
            <planeGeometry args={[1.4, 1.0]} />
            <meshStandardMaterial
              color="#0e1730"
              emissive="#7a8eff"
              emissiveIntensity={0.7}
              roughness={0.4}
            />
          </mesh>
          {/* moon */}
          <mesh position={[0.02, 0.1, 0]} rotation={[0, Math.PI / 2, 0]}>
            <circleGeometry args={[0.18, 24]} />
            <meshBasicMaterial color="#f6efc8" />
          </mesh>
          {/* mullion */}
          <mesh rotation={[0, Math.PI / 2, 0]} position={[0.001, 0, 0]}>
            <planeGeometry args={[1.4, 0.04]} />
            <meshStandardMaterial color="#241f3c" />
          </mesh>
          <mesh rotation={[0, Math.PI / 2, 0]} position={[0.001, 0, 0]}>
            <planeGeometry args={[0.04, 1.0]} />
            <meshStandardMaterial color="#241f3c" />
          </mesh>
        </group>
      )}

      {/* hanging lamp */}
      <group position={[0, ROOM_H - 0.05, 0]}>
        <mesh>
          <cylinderGeometry args={[0.05, 0.05, 0.5, 12]} />
          <meshStandardMaterial color="#241f3c" />
        </mesh>
        <mesh position={[0, -0.35, 0]}>
          <coneGeometry args={[0.28, 0.3, 18]} />
          <meshStandardMaterial
            color="#2c2745"
            emissive="#fff2c4"
            emissiveIntensity={0.4}
          />
        </mesh>
      </group>

      {/* objects */}
      {placed.map((p) => (
        <PlacedObjectNode
          key={p.id}
          obj={p}
          accent={R.accent}
          rm={rm}
          onTap={onTap}
          onObjectFocus={onObjectFocus}
          doorSwing={doorSwing}
        />
      ))}
    </group>
  );
}

function PlacedObjectNode({
  obj,
  accent,
  rm,
  onTap,
  onObjectFocus,
  doorSwing,
}: {
  obj: PlacedObject;
  accent: string;
  rm: RoomId;
  onTap: (id: string) => void;
  onObjectFocus: (eye: [number, number, number] | null, target: [number, number, number] | null) => void;
  doorSwing: any;
}) {
  const isExitDoor = obj.isExit;
  const [px, py, pz] = obj.position;
  const eye: [number, number, number] = [px * 0.7, py + 0.4, pz + 2.4];
  const tgt: [number, number, number] = [px, py, pz];

  const baseRot: [number, number, number] = obj.rotation;
  const accentBase = obj.state.cls === 'sealed' ? 0.3 : 1;

  return (
    <group
      position={obj.position}
      rotation={baseRot}
      onClick={(e) => {
        e.stopPropagation();
        if (obj.state.cls === 'sealed') {
          onTap(obj.id); // store will toast
          return;
        }
        if (obj.state.cls === 'done' && obj.type === 'find') {
          onTap(obj.id);
          return;
        }
        onTap(obj.id);
        onObjectFocus(eye, tgt);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        if (typeof document !== 'undefined') {
          document.body.style.cursor = obj.state.cls === 'sealed' ? 'not-allowed' : 'pointer';
        }
      }}
      onPointerOut={() => {
        if (typeof document !== 'undefined') document.body.style.cursor = 'auto';
      }}
    >
      {isExitDoor ? (
        <animated.group rotation-y={doorSwing.rotY}>
          <group position={[getSpec(obj.art).size[0] / 2, 0, 0]}>
            <group position={[-getSpec(obj.art).size[0] / 2, 0, 0]}>
              <Furniture art={obj.art} accent={accent} state={obj.state.cls} />
            </group>
          </group>
        </animated.group>
      ) : (
        <Furniture art={obj.art} accent={accent} state={obj.state.cls} />
      )}
      <Html
        position={[0, getSpec(obj.art).size[1] / 2 + 0.45, 0]}
        center
        distanceFactor={8}
        zIndexRange={[10, 0]}
        pointerEvents="none"
      >
        <div
          className="px-2.5 py-1 rounded-lg bg-black/70 text-white text-center min-w-[88px] select-none"
          style={{
            border: `1px solid ${obj.state.cls === 'sealed' ? 'rgba(255,255,255,0.2)' : accent}`,
            opacity: obj.state.cls === 'sealed' ? 0.55 : 1,
          }}
        >
          <div className="text-[12.5px] font-semibold leading-tight">{obj.label}</div>
          <div
            className="text-[10px] uppercase font-bold tracking-wider"
            style={{
              color:
                obj.state.cls === 'live'
                  ? accent
                  : obj.state.cls === 'open'
                    ? '#7ee6b4'
                    : obj.state.cls === 'done'
                      ? '#8de0a8'
                      : 'rgba(255,255,255,0.6)',
            }}
          >
            {obj.state.sub}
          </div>
        </div>
      </Html>
      {/* silent dependency to keep accentBase referenced for tree-shakers */}
      <group userData={{ a: accentBase, rm }} />
    </group>
  );
}
