import React, { useRef, useImperativeHandle, forwardRef } from 'react';
import confetti from 'canvas-confetti';

const ConfettiCanvas = forwardRef(function ConfettiCanvas({ manualstart = false, ...props }, ref) {
  const canvasRef = useRef(null);
  const confettiInstanceRef = useRef(null);

  function getConfettiInstance() {
    if (!canvasRef.current) return null;
    if (!confettiInstanceRef.current) {
      confettiInstanceRef.current = confetti.create(canvasRef.current, {
        resize: true,
        useWorker: true,
      });
    }
    return confettiInstanceRef.current;
  }

  useImperativeHandle(ref, () => ({
    fire(options) {
      const instance = getConfettiInstance();
      if (!instance) return;

      const defaults = {
        particleCount: 60,
        spread: 55,
        colors: ['#e8412a', '#c9341f', '#f4b5ad', '#1a1208', '#e0d8c8'],
      };

      // Left cannon
      instance({
        ...defaults,
        ...options,
        angle: 60,
        origin: { x: 0, y: 0.65 },
      });

      // Right cannon
      instance({
        ...defaults,
        ...options,
        angle: 120,
        origin: { x: 1, y: 0.65 },
      });
    },
  }));

  return (
    <canvas
      ref={canvasRef}
      {...props}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 999,
        ...props.style,
      }}
    />
  );
});

export { ConfettiCanvas };
