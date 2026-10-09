import { useCallback, useEffect, useRef, useState } from 'react';
import { autoHide, type AutoHide } from '../domain/autoHide';

/** Visible at the top and after scrolling up; hidden while scrolling down. `floating` = off the top. */
export function useAutoHide(): { visible: boolean; floating: boolean; show: () => void } {
  const state = useRef<AutoHide>({ visible: true, anchor: window.scrollY });
  const [visible, setVisible] = useState(true);
  const [floating, setFloating] = useState(false);
  useEffect(() => {
    const onScroll = () => {
      state.current = autoHide(state.current, window.scrollY);
      setVisible(state.current.visible);
      setFloating(window.scrollY > 0);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  const show = useCallback(() => {
    state.current = { visible: true, anchor: window.scrollY };
    setVisible(true);
  }, []);
  return { visible, floating, show };
}
