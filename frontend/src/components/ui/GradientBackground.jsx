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
      {/* Base warm cream background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(135deg, var(--cream) 0%, var(--cream-dark) 60%, var(--cream-darker) 100%)',
        }}
      />

      {/* Large coral orb — top right */}
      <div
        style={{
          position: 'absolute',
          top: '-15%',
          right: '-10%',
          width: '55vw',
          height: '55vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(232,65,42,0.18) 0%, rgba(201,52,31,0.08) 50%, transparent 70%)',
          filter: 'blur(40px)',
        }}
      />

      {/* Medium coral orb — bottom left */}
      <div
        style={{
          position: 'absolute',
          bottom: '-10%',
          left: '-8%',
          width: '45vw',
          height: '45vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(232,65,42,0.14) 0%, rgba(244,181,173,0.06) 50%, transparent 70%)',
          filter: 'blur(50px)',
        }}
      />

      {/* Subtle warm center glow */}
      <div
        style={{
          position: 'absolute',
          top: '40%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '60vw',
          height: '60vw',
          borderRadius: '50%',
          background:
            'radial-gradient(circle, rgba(245,240,232,0.4) 0%, transparent 60%)',
          filter: 'blur(60px)',
        }}
      />

      {/* Noise texture overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.025,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
          backgroundSize: '128px 128px',
        }}
      />
    </div>
  );
}
