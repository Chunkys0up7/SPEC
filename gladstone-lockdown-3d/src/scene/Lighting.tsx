import { useMemo } from 'react';

interface Props {
  accent: string;
  hasWindow: boolean;
}

export default function Lighting({ accent, hasWindow }: Props) {
  const lampPos: [number, number, number] = useMemo(() => [0, 2.7, 0], []);
  return (
    <>
      <ambientLight intensity={0.18} />
      <hemisphereLight args={['#3a3060', '#0e0a1a', 0.35]} />

      {/* lamp */}
      <pointLight
        position={lampPos}
        intensity={1.5}
        distance={9}
        decay={1.4}
        color="#fff7e0"
        castShadow
      />
      {/* warm cone visual */}
      <mesh position={[0, 1.5, 0]} rotation={[0, 0, 0]}>
        <coneGeometry args={[1.6, 2.2, 24, 1, true]} />
        <meshBasicMaterial color={accent} transparent opacity={0.05} depthWrite={false} />
      </mesh>

      {/* moonlight through window for Room 1 / 3 */}
      {hasWindow && (
        <directionalLight
          position={[-4, 3, 4]}
          intensity={0.45}
          color="#9bb6ff"
          castShadow={false}
        />
      )}

      {/* subtle accent fill */}
      <pointLight position={[2.5, 1.4, -2]} intensity={0.25} color={accent} distance={6} />
    </>
  );
}
