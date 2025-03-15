import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh } from 'three';

interface RingProps {
  radius: [number, number];
  segments: number;
  speed: number;
  opacity: number;
  emissiveIntensity: number;
}

const StatusRings: React.FC = () => {
  const ringRefs = [
    useRef<Mesh>(null),
    useRef<Mesh>(null),
    useRef<Mesh>(null)
  ];

  useFrame((_, delta) => {
    ringRefs.forEach((ref, index) => {
      if (ref.current) {
        ref.current.rotation.z += delta * (index === 1 ? -0.15 : 0.1 * (index + 1));
      }
    });
  });

  const rings: RingProps[] = [
    { radius: [3, 3.1], segments: 128, speed: 0.1, opacity: 0.4, emissiveIntensity: 0.3 },
    { radius: [2.6, 2.7], segments: 96, speed: 0.15, opacity: 0.5, emissiveIntensity: 0.4 },
    { radius: [2.3, 2.4], segments: 64, speed: 0.2, opacity: 0.7, emissiveIntensity: 0.6 }
  ];

  const decorativeElements = Array.from({ length: 8 }, (_, index) => {
    const angle = (Math.PI * 2 * index) / 8;
    const position: [number, number, number] = [
      Math.cos(angle) * 3.2,
      Math.sin(angle) * 3.2,
      0
    ];
    
    return (
      <mesh
        key={`decoration-${index}`}
        rotation={[0, 0, angle]}
        position={position}
      >
        <boxGeometry args={[0.1, 0.1, 0.01]} />
        <meshStandardMaterial
          color="#00a2ff"
          emissive="#00a2ff"
          emissiveIntensity={0.5}
          transparent
          opacity={0.8}
        />
      </mesh>
    );
  });

  return (
    <group>
      {rings.map((ring, index) => (
        <mesh key={`ring-${index}`} ref={ringRefs[index]}>
          <ringGeometry args={[ring.radius[0], ring.radius[1], ring.segments]} />
          <meshStandardMaterial
            color="#00a2ff"
            emissive="#00a2ff"
            emissiveIntensity={ring.emissiveIntensity}
            transparent
            opacity={ring.opacity}
          />
        </mesh>
      ))}

      {decorativeElements}
    </group>
  );
};

export default StatusRings;