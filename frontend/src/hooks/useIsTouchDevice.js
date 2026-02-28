export function useIsTouchDevice() {
  return window.matchMedia('(hover: none) and (pointer: coarse)').matches;
}
