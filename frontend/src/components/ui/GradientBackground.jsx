import React from 'react';

export function GradientBackground() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
    >
      {/* Dark base */}
      <div style={{ position: 'absolute', inset: 0, background: '#0d0d0f' }} />

      {/* Top-right: coral → purple */}
      <div
        style={{
          position: 'absolute',
          top: '-20%',
          right: '-15%',
          width: '65vw',
          height: '65vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(232,65,38,0.80) 0%, rgba(124,58,237,0.60) 50%, transparent 75%)',
          filter: 'blur(55px)',
          opacity: 0.8,
        }}
      />

      {/* Bottom-left: amber → pink → coral */}
      <div
        style={{
          position: 'absolute',
          bottom: '-15%',
          left: '-12%',
          width: '58vw',
          height: '58vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(245,158,11,0.70) 0%, rgba(236,72,153,0.55) 40%, rgba(232,65,38,0.45) 65%, transparent 85%)',
          filter: 'blur(40px)',
          opacity: 0.85,
        }}
      />

      {/* Center: dark red → dark purple */}
      <div
        style={{
          position: 'absolute',
          top: '38%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '52vw',
          height: '52vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(220,38,38,0.45) 0%, rgba(76,29,149,0.38) 55%, transparent 80%)',
          filter: 'blur(65px)',
          opacity: 0.75,
        }}
      />

      {/* Bottom center: blue */}
      <div
        style={{
          position: 'absolute',
          bottom: '2%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '42vw',
          height: '22vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(29,78,216,0.55) 0%, transparent 70%)',
          filter: 'blur(45px)',
          opacity: 0.65,
        }}
      />

      {/* Blur overlay + darkening layer — sits between gradients and content */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backdropFilter: 'blur(80px)',
          WebkitBackdropFilter: 'blur(80px)',
          background: 'rgba(13, 13, 15, 0.45)',
        }}
      />
    </div>
  );
}
