import { useEffect, useLayoutEffect, useRef } from 'react';

/**
 * Watches `[data-block]` children of `root` and reports the topmost visible block index
 * (throttled) and when the final block first becomes visible.
 */
export function useReadingTracker(
  root: HTMLElement | null,
  blockCount: number,
  onTopmost: (index: number) => void,
  onFinal: () => void,
  throttleMs = 800,
) {
  const cbs = useRef({ onTopmost, onFinal });
  useLayoutEffect(() => {
    cbs.current = { onTopmost, onFinal };
  });

  useEffect(() => {
    if (!root || blockCount === 0 || typeof IntersectionObserver === 'undefined') return;
    const visible = new Set<number>();
    let finalSeen = false;
    let timer: ReturnType<typeof setTimeout> | null = null;
    let last = -1;

    const flush = () => {
      timer = null;
      if (visible.size === 0) return;
      const top = Math.min(...visible);
      if (top !== last) {
        last = top;
        cbs.current.onTopmost(top);
      }
    };

    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const i = Number((e.target as HTMLElement).dataset.block);
        if (e.isIntersecting) visible.add(i);
        else visible.delete(i);
        if (e.isIntersecting && i === blockCount - 1 && !finalSeen) {
          finalSeen = true;
          cbs.current.onFinal();
        }
      }
      timer ??= setTimeout(flush, throttleMs);
    });
    root.querySelectorAll<HTMLElement>('[data-block]').forEach((el) => io.observe(el));
    return () => {
      io.disconnect();
      if (timer) clearTimeout(timer);
    };
  }, [root, blockCount, throttleMs]);
}
