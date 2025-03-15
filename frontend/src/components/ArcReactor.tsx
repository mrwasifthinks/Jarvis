import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh, BufferAttribute, Float32BufferAttribute, Color } from 'three';

const ArcReactor: React.FC = () => {
  const outerRingRef = useRef<Mesh>(null);
  const innerRingRef = useRef<Mesh>(null);
  const coreRef = useRef<Mesh>(null);
  const particlesRef = useRef<any>(null);

  const particlesPosition = useMemo(() => {
    const positions = new Float32Array(6000);
    for (let i = 0; i < positions.length; i += 3) {
      const radius = Math.random() * 3;
      const theta = Math.random() * Math.PI * 2;
      positions[i] = radius * Math.cos(theta);
      positions[i + 1] = radius * Math.sin(theta);
      positions[i + 2] = (Math.random() - 0.5) * 0.5;
    }
    return new Float32BufferAttribute(positions, 3);
  }, []);

  useFrame((state, delta) => {
    if (outerRingRef.current) {
      outerRingRef.current.rotation.z += delta * 0.2;
      outerRingRef.current.scale.x = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.05;
      outerRingRef.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.05;
    }
    if (innerRingRef.current) {
      innerRingRef.current.rotation.z -= delta * 0.3;
      innerRingRef.current.scale.x = 1 + Math.cos(state.clock.elapsedTime * 0.7) * 0.03;
      innerRingRef.current.scale.y = 1 + Math.cos(state.clock.elapsedTime * 0.7) * 0.03;
    }
    if (coreRef.current) {
      coreRef.current.scale.x = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
      coreRef.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
    }
    if (particlesRef.current) {
      particlesRef.current.rotation.z += delta * 0.1;
      const positions = particlesRef.current.geometry.attributes.position.array;
      for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i];
        const y = positions[i + 1];
        const angle = Math.atan2(y, x) + delta * 0.2;
        const radius = Math.sqrt(x * x + y * y);
        positions[i] = radius * Math.cos(angle);
        positions[i + 1] = radius * Math.sin(angle);
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <group>
      {/* Outer Ring */}
      <mesh ref={outerRingRef}>
        <ringGeometry args={[2, 2.2, 64]} />
        <meshStandardMaterial
          color="#00a2ff"
          emissive="#00a2ff"
          emissiveIntensity={1}
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Inner Ring */}
      <mesh ref={innerRingRef}>
        <ringGeometry args={[1.2, 1.4, 32]} />
        <meshStandardMaterial
          color="#00a2ff"
          emissive="#00a2ff"
          emissiveIntensity={1.2}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Core */}
      <mesh ref={coreRef}>
        <circleGeometry args={[0.8, 32]} />
        <meshStandardMaterial
          color="#00a2ff"
          emissive="#00a2ff"
          emissiveIntensity={1.5}
          transparent
          opacity={1}
        />
      </mesh>

      {/* Energy Particles */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            {...particlesPosition}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.02}
          color="#00a2ff"
          transparent
          opacity={0.8}
          sizeAttenuation
          blending={2}
        />
      </points>
    </group>
  );
};

export default ArcReactor;