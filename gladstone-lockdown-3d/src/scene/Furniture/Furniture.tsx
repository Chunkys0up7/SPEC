import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import type { Group, Mesh, MeshStandardMaterial } from 'three';
import type { ArtType, SpotClass } from '@/game/types';

interface FurnitureProps {
  art: ArtType;
  accent: string;
  state: SpotClass;
  highlightOnHover?: boolean;
}

interface Spec {
  size: [number, number, number]; // w, h, d
  wallMounted: boolean;
  body: 'box' | 'cylinder' | 'tall' | 'mug' | 'plant';
  bodyColor: string;
  details?: 'screen' | 'keypad' | 'dial' | 'shelves' | 'rings' | 'tray' | 'fan' | 'door' | 'register';
  emoji?: string;
}

const SPECS: Record<ArtType, Spec> = {
  door:     { size: [1.1, 2.2, 0.18], wallMounted: false, body: 'box',   bodyColor: '#2c2745', details: 'door',     emoji: '🚪' },
  vault:    { size: [1.5, 2.0, 0.6],  wallMounted: false, body: 'box',   bodyColor: '#2a2540', details: 'dial',     emoji: '🔐' },
  elevator: { size: [1.6, 2.3, 0.25], wallMounted: false, body: 'box',   bodyColor: '#2c2745', details: 'door',     emoji: '🛗' },
  cabinet:  { size: [1.0, 1.7, 0.55], wallMounted: false, body: 'tall',  bodyColor: '#3b3358', details: 'shelves',  emoji: '🗄️' },
  drawer:   { size: [1.3, 0.9, 0.55], wallMounted: false, body: 'box',   bodyColor: '#5a4a36', details: 'tray',     emoji: '🗄️' },
  safe:     { size: [1.05, 1.05, 0.55], wallMounted: false, body: 'box', bodyColor: '#2c2842', details: 'dial',     emoji: '🔐' },
  wallsafe: { size: [0.95, 0.85, 0.18], wallMounted: true,  body: 'box', bodyColor: '#2c2842', details: 'dial',     emoji: '🔐' },
  register: { size: [1.05, 1.0, 0.55], wallMounted: false, body: 'box',  bodyColor: '#33304d', details: 'register', emoji: '💳' },
  monitor:  { size: [1.3, 1.0, 0.4],  wallMounted: false, body: 'box',   bodyColor: '#1b1830', details: 'screen',   emoji: '🖥️' },
  phone:    { size: [1.0, 0.6, 0.4],  wallMounted: false, body: 'box',   bodyColor: '#2c2745', details: 'keypad',   emoji: '📞' },
  fax:      { size: [1.1, 0.85, 0.5], wallMounted: false, body: 'box',   bodyColor: '#33304d', details: 'tray',     emoji: '📠' },
  mug:      { size: [0.4, 0.45, 0.4], wallMounted: false, body: 'mug',   bodyColor: '#d8d2ec',                       emoji: '☕' },
  calc:     { size: [0.55, 0.75, 0.15], wallMounted: false, body: 'box', bodyColor: '#2c2745', details: 'keypad',   emoji: '🧮' },
  box:      { size: [0.8, 0.6, 0.6],  wallMounted: false, body: 'box',   bodyColor: '#6b5a3e',                        emoji: '📦' },
  plant:    { size: [0.7, 1.2, 0.7],  wallMounted: false, body: 'plant', bodyColor: '#3f8a4e',                        emoji: '🪴' },
  shredder: { size: [0.85, 1.1, 0.6], wallMounted: false, body: 'tall',  bodyColor: '#2f2a48', details: 'fan',       emoji: '🗑️' },
  binder:   { size: [1.4, 0.85, 0.18], wallMounted: true,  body: 'box',  bodyColor: '#3a2f1d', details: 'shelves',  emoji: '📚' },
  whiteboard: { size: [1.6, 1.05, 0.06], wallMounted: true, body: 'box', bodyColor: '#f3f0ff',                       emoji: '🧾' },
  poster:   { size: [1.2, 0.9, 0.04], wallMounted: true,  body: 'box',   bodyColor: '#262040',                        emoji: '📣' },
  frame:    { size: [1.1, 0.9, 0.06], wallMounted: true,  body: 'box',   bodyColor: '#2a2444',                        emoji: '🖼️' },
  panel:    { size: [0.8, 1.2, 0.08], wallMounted: true,  body: 'box',   bodyColor: '#2c2745', details: 'keypad',    emoji: '⌨️' },
  sticky:   { size: [0.4, 0.4, 0.02], wallMounted: true,  body: 'box',   bodyColor: '#ffe066',                        emoji: '📝' },
  sheet:    { size: [0.7, 0.6, 0.04], wallMounted: false, body: 'box',   bodyColor: '#fbf9ff',                        emoji: '📄' },
  folder:   { size: [0.8, 0.6, 0.04], wallMounted: false, body: 'box',   bodyColor: '#e7b75c',                        emoji: '📁' },
};

export function isWallMounted(art: ArtType): boolean {
  return SPECS[art].wallMounted;
}

export function getSpec(art: ArtType): Spec {
  return SPECS[art];
}

const PRM = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false;

export default function Furniture({ art, accent, state }: FurnitureProps) {
  const spec = SPECS[art];
  const group = useRef<Group>(null);
  const accentMat = useRef<MeshStandardMaterial>(null);
  const bodyMesh = useRef<Mesh>(null);

  // pulse on live, dim on sealed/done
  useFrame((stt) => {
    if (PRM) return;
    if (!accentMat.current) return;
    if (state === 'live') {
      const t = stt.clock.getElapsedTime();
      const pulse = 0.4 + 0.4 * (Math.sin((t * 2 * Math.PI) / 1.7) * 0.5 + 0.5) * 2;
      accentMat.current.emissiveIntensity = pulse;
    } else if (state === 'open') {
      accentMat.current.emissiveIntensity = 0.7;
    } else {
      accentMat.current.emissiveIntensity = 0.15;
    }
  });

  const [w, h, d] = spec.size;
  const dim = state === 'sealed' ? 0.5 : state === 'done' ? 0.55 : 1;
  const tint = state === 'done' ? '#3a7d57' : spec.bodyColor;
  const roughness = 0.85;

  return (
    <group ref={group}>
      {/* main body */}
      {spec.body === 'box' && (
        <mesh ref={bodyMesh} castShadow receiveShadow>
          <boxGeometry args={[w, h, d]} />
          <meshStandardMaterial
            color={tint}
            roughness={roughness}
            metalness={0.05}
            opacity={dim}
            transparent={dim < 1}
          />
        </mesh>
      )}
      {spec.body === 'tall' && (
        <mesh castShadow receiveShadow>
          <boxGeometry args={[w, h, d]} />
          <meshStandardMaterial color={tint} roughness={roughness} opacity={dim} transparent={dim < 1} />
        </mesh>
      )}
      {spec.body === 'cylinder' && (
        <mesh castShadow receiveShadow>
          <cylinderGeometry args={[w / 2, w / 2, h, 24]} />
          <meshStandardMaterial color={tint} roughness={roughness} opacity={dim} transparent={dim < 1} />
        </mesh>
      )}
      {spec.body === 'mug' && (
        <group>
          <mesh castShadow receiveShadow position={[0, 0, 0]}>
            <cylinderGeometry args={[w / 2, w / 2.2, h, 24]} />
            <meshStandardMaterial color={tint} roughness={0.45} opacity={dim} transparent={dim < 1} />
          </mesh>
          <mesh castShadow position={[w / 2 + 0.04, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
            <torusGeometry args={[h * 0.32, h * 0.06, 8, 18, Math.PI]} />
            <meshStandardMaterial color={tint} roughness={0.45} opacity={dim} transparent={dim < 1} />
          </mesh>
        </group>
      )}
      {spec.body === 'plant' && (
        <group>
          <mesh castShadow receiveShadow position={[0, -h / 2 + 0.15, 0]}>
            <cylinderGeometry args={[w / 2.2, w / 2.6, 0.3, 16]} />
            <meshStandardMaterial color="#5e3f24" roughness={0.9} opacity={dim} transparent={dim < 1} />
          </mesh>
          <mesh position={[0, h / 4, 0]} castShadow>
            <icosahedronGeometry args={[h / 2.2, 1]} />
            <meshStandardMaterial color={tint} roughness={0.7} opacity={dim} transparent={dim < 1} />
          </mesh>
        </group>
      )}

      {/* details */}
      {spec.details === 'screen' && (
        <mesh position={[0, 0.05, d / 2 + 0.001]}>
          <planeGeometry args={[w * 0.85, h * 0.65]} />
          <meshStandardMaterial
            color="#0e1626"
            emissive={accent}
            emissiveIntensity={0.35}
            roughness={0.4}
            opacity={dim}
            transparent={dim < 1}
          />
        </mesh>
      )}
      {spec.details === 'keypad' && (
        <group position={[0, 0, d / 2 + 0.005]}>
          {Array.from({ length: 12 }).map((_, i) => {
            const col = i % 3;
            const row = Math.floor(i / 3);
            const kw = w * 0.18;
            return (
              <mesh
                key={i}
                position={[(col - 1) * (w * 0.26), (row - 1.5) * (h * 0.18) + h * 0.05, 0]}
              >
                <boxGeometry args={[kw, kw * 0.9, 0.02]} />
                <meshStandardMaterial color="#52496f" roughness={0.6} opacity={dim} transparent={dim < 1} />
              </mesh>
            );
          })}
        </group>
      )}
      {spec.details === 'dial' && (
        <group position={[0, 0, d / 2 + 0.01]}>
          <mesh>
            <torusGeometry args={[Math.min(w, h) * 0.28, Math.min(w, h) * 0.04, 12, 32]} />
            <meshStandardMaterial
              color={accent}
              emissive={accent}
              emissiveIntensity={0.5}
              roughness={0.5}
              metalness={0.4}
              opacity={dim}
              transparent={dim < 1}
            />
          </mesh>
          <mesh position={[Math.min(w, h) * 0.12, 0, 0.01]} rotation={[0, 0, Math.PI / 6]}>
            <boxGeometry args={[Math.min(w, h) * 0.28, 0.04, 0.02]} />
            <meshStandardMaterial color="#fff" emissiveIntensity={0.2} />
          </mesh>
        </group>
      )}
      {spec.details === 'shelves' && (
        <group>
          {Array.from({ length: 3 }).map((_, i) => (
            <mesh key={i} position={[0, h / 2 - 0.25 - i * (h / 3.2), d / 2 - 0.02]}>
              <boxGeometry args={[w * 0.86, 0.04, 0.05]} />
              <meshStandardMaterial color="#1c1838" />
            </mesh>
          ))}
        </group>
      )}
      {spec.details === 'tray' && (
        <mesh position={[0, h / 2 + 0.04, 0]}>
          <boxGeometry args={[w * 0.8, 0.06, d * 0.7]} />
          <meshStandardMaterial color="#454069" roughness={0.7} opacity={dim} transparent={dim < 1} />
        </mesh>
      )}
      {spec.details === 'fan' && (
        <mesh position={[0, h / 2 - 0.04, 0]}>
          <boxGeometry args={[w * 0.5, 0.04, d * 0.4]} />
          <meshStandardMaterial color="#12101f" />
        </mesh>
      )}
      {spec.details === 'door' && (
        <group>
          <mesh position={[w / 4, 0, d / 2 + 0.01]}>
            <boxGeometry args={[0.08, 0.2, 0.06]} />
            <meshStandardMaterial
              color={accent}
              emissive={accent}
              emissiveIntensity={0.6}
              roughness={0.4}
            />
          </mesh>
          <mesh position={[0, h / 2 - 0.4, d / 2 + 0.005]}>
            <boxGeometry args={[w * 0.7, 0.5, 0.005]} />
            <meshStandardMaterial color="#241f3c" />
          </mesh>
        </group>
      )}
      {spec.details === 'register' && (
        <mesh position={[0, h * 0.15, d / 2 + 0.001]}>
          <planeGeometry args={[w * 0.7, h * 0.25]} />
          <meshStandardMaterial color="#9fe0c0" emissive={accent} emissiveIntensity={0.3} />
        </mesh>
      )}

      {/* accent ring / glow plate — emits with accent color, drives pulse */}
      {!spec.wallMounted && (
        <mesh position={[0, -h / 2 - 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]} renderOrder={2}>
          <ringGeometry args={[Math.max(w, d) * 0.55, Math.max(w, d) * 0.62, 32]} />
          <meshStandardMaterial
            ref={accentMat}
            color={accent}
            emissive={accent}
            emissiveIntensity={state === 'live' ? 0.8 : state === 'open' ? 0.7 : 0.15}
            transparent
            opacity={state === 'sealed' ? 0.2 : state === 'done' ? 0.25 : 0.85}
          />
        </mesh>
      )}
      {spec.wallMounted && (
        <mesh position={[0, 0, -d / 2 - 0.01]} renderOrder={2}>
          <planeGeometry args={[w + 0.2, h + 0.2]} />
          <meshStandardMaterial
            ref={accentMat}
            color={accent}
            emissive={accent}
            emissiveIntensity={state === 'live' ? 0.6 : state === 'open' ? 0.5 : 0.1}
            transparent
            opacity={state === 'sealed' ? 0.1 : state === 'done' ? 0.18 : 0.45}
          />
        </mesh>
      )}
    </group>
  );
}
