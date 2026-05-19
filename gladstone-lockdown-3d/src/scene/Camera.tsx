import { useEffect, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { useSpring, animated } from '@react-spring/three';
import * as THREE from 'three';

interface Props {
  focusTarget: [number, number, number] | null;
  focusEye: [number, number, number] | null;
  enableOrbit: boolean;
}

const DEFAULT_EYE: [number, number, number] = [0, 1.7, 5.5];
const DEFAULT_TGT: [number, number, number] = [0, 1.4, 0];

const PRM =
  typeof window !== 'undefined' && window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

export default function CameraRig({ focusTarget, focusEye, enableOrbit }: Props) {
  const { camera } = useThree();
  const controls = useRef<any>(null);

  const eye = focusEye ?? DEFAULT_EYE;
  const tgt = focusTarget ?? DEFAULT_TGT;

  const spring = useSpring({
    px: eye[0],
    py: eye[1],
    pz: eye[2],
    tx: tgt[0],
    ty: tgt[1],
    tz: tgt[2],
    config: { mass: 1, tension: 120, friction: 28 },
    immediate: PRM,
  });

  // apply spring to camera each frame
  useEffect(() => {
    const tick = () => {
      camera.position.set(spring.px.get(), spring.py.get(), spring.pz.get());
      if (controls.current) {
        controls.current.target.set(spring.tx.get(), spring.ty.get(), spring.tz.get());
        controls.current.update();
      } else {
        camera.lookAt(new THREE.Vector3(spring.tx.get(), spring.ty.get(), spring.tz.get()));
      }
    };
    const id = setInterval(tick, 16);
    return () => clearInterval(id);
  }, [camera, spring.px, spring.py, spring.pz, spring.tx, spring.ty, spring.tz]);

  return (
    <>
      <animated.group />
      <OrbitControls
        ref={controls}
        enabled={enableOrbit}
        enableDamping
        dampingFactor={0.08}
        minPolarAngle={(60 * Math.PI) / 180}
        maxPolarAngle={(85 * Math.PI) / 180}
        minDistance={3.5}
        maxDistance={8}
        target={[DEFAULT_TGT[0], DEFAULT_TGT[1], DEFAULT_TGT[2]]}
      />
    </>
  );
}

export { DEFAULT_EYE, DEFAULT_TGT };
