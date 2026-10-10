import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

if (typeof window !== 'undefined') {
  window.scrollTo = () => {};
  // jsdom lacks PointerEvent; MouseEvent carries the clientX/Y the swipe code reads.
  if (!('PointerEvent' in window)) {
    class PointerEvent extends MouseEvent {
      pointerId: number;
      pointerType: string;
      constructor(type: string, init: PointerEventInit = {}) {
        super(type, init);
        this.pointerId = init.pointerId ?? 0;
        this.pointerType = init.pointerType ?? '';
      }
    }
    Object.assign(window, { PointerEvent });
  }
}

afterEach(() => {
  if (typeof window === 'undefined') return;
  cleanup();
  localStorage.clear();
});
