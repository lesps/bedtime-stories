import { useEffect, useRef, useState, type PointerEvent } from 'react';

const OPEN_EVENT = 'storyrow:open';
const SLOP = 10;

/**
 * Horizontal swipe-left to reveal a fixed-width action tray. Vertical gestures are left to the
 * browser (pair with `touch-action: pan-y`). Only one row is open at a time.
 */
export function useSwipeReveal(id: string, width: number) {
  const [offset, setOffset] = useState(0);
  const [open, setOpenState] = useState(false);
  const [dragging, setDragging] = useState(false);
  const gesture = useRef<{ x: number; y: number; base: number; axis: 'x' | 'y' | null } | null>(
    null,
  );
  const swiped = useRef(false);

  const setOpen = (next: boolean) => {
    setOpenState(next);
    setOffset(next ? -width : 0);
    if (next) window.dispatchEvent(new CustomEvent(OPEN_EVENT, { detail: id }));
  };

  useEffect(() => {
    const onOther = (e: Event) => {
      if ((e as CustomEvent<string>).detail === id) return;
      setOpenState(false);
      setOffset(0);
    };
    window.addEventListener(OPEN_EVENT, onOther);
    return () => window.removeEventListener(OPEN_EVENT, onOther);
  }, [id]);

  const handlers = {
    onPointerDown(e: PointerEvent<HTMLElement>) {
      if (e.button !== 0) return;
      swiped.current = false;
      gesture.current = { x: e.clientX, y: e.clientY, base: open ? -width : 0, axis: null };
    },
    onPointerMove(e: PointerEvent<HTMLElement>) {
      const g = gesture.current;
      if (!g) return;
      const dx = e.clientX - g.x;
      const dy = e.clientY - g.y;
      if (!g.axis) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) < SLOP) return;
        g.axis = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
        if (g.axis === 'x') {
          swiped.current = true;
          setDragging(true);
          e.currentTarget.setPointerCapture?.(e.pointerId);
        }
      }
      if (g.axis === 'x') setOffset(Math.max(-width, Math.min(0, g.base + dx)));
    },
    onPointerUp(e: PointerEvent<HTMLElement>) {
      const g = gesture.current;
      gesture.current = null;
      setDragging(false);
      if (!g || g.axis !== 'x') return;
      setOpen(g.base + (e.clientX - g.x) < -width / 2);
    },
    onPointerCancel() {
      gesture.current = null;
      setDragging(false);
      setOffset(open ? -width : 0);
    },
    /** Swallow the click that ends a swipe, and a tap on an open row just closes it. */
    onClickCapture(e: React.MouseEvent) {
      if (!swiped.current && !open) return;
      e.preventDefault();
      e.stopPropagation();
      if (!swiped.current) setOpen(false);
      swiped.current = false;
    },
  };

  return { offset, open, dragging, setOpen, handlers };
}
