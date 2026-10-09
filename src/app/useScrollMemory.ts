import { useEffect, useLayoutEffect, useRef } from 'react';
import { useLocation, useNavigationType } from 'react-router';

const positions = new Map<string, number>();

/**
 * New pages start at the top; Back/Forward return to where that history entry was left.
 * Keyed by history entry, and only reacting to path changes, so query-only updates
 * (`?notes=1`, `?by=`) never move the page.
 */
export function useScrollMemory() {
  const { key, pathname } = useLocation();
  const type = useNavigationType();
  const current = useRef(key);
  // Layout effects run in the same task as the DOM update, before the scroll event a shorter new
  // page triggers, so that clamp is never saved against the page being left.
  useLayoutEffect(() => {
    current.current = key;
  });
  useEffect(() => {
    history.scrollRestoration = 'manual';
    const save = () => positions.set(current.current, window.scrollY);
    window.addEventListener('scroll', save, { passive: true });
    return () => window.removeEventListener('scroll', save);
  }, []);
  useLayoutEffect(() => {
    const saved = type === 'POP' ? positions.get(key) : undefined;
    window.scrollTo(0, saved ?? 0);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only on page changes
  }, [pathname]);
}
