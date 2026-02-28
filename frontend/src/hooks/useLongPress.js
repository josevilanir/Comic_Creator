import { useRef, useCallback } from 'react';

export function useLongPress(onLongPress, delay = 500) {
  const timerRef    = useRef(null);
  const isLongPress = useRef(false);

  const start = useCallback((e) => {
    isLongPress.current = false;
    timerRef.current = setTimeout(() => {
      isLongPress.current = true;
      onLongPress(e);
    }, delay);
  }, [onLongPress, delay]);

  const stop = useCallback(() => {
    clearTimeout(timerRef.current);
  }, []);

  return {
    onMouseDown:  start,
    onMouseUp:    stop,
    onMouseLeave: stop,
    onTouchStart: start,
    onTouchEnd:   stop,
  };
}
