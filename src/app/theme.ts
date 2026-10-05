import { useEffect, useSyncExternalStore } from 'react';
import type { Theme } from '../storage/store';

export type ResolvedTheme = Exclude<Theme, 'system'>;

/** Kept in sync with the --bg tokens in styles.css. */
export const THEME_COLORS: Record<ResolvedTheme, string> = {
  light: '#ffffff',
  sepia: '#f6efe1',
  dark: '#15161a',
};

export function resolveTheme(setting: Theme, prefersDark: boolean): ResolvedTheme {
  if (setting !== 'system') return setting;
  return prefersDark ? 'dark' : 'sepia';
}

function mediaStore(query: string) {
  return {
    subscribe(cb: () => void) {
      const mql = window.matchMedia?.(query);
      mql?.addEventListener('change', cb);
      return () => mql?.removeEventListener('change', cb);
    },
    get: () => window.matchMedia?.(query).matches ?? false,
  };
}
const darkQuery = mediaStore('(prefers-color-scheme: dark)');
const reducedMotionQuery = mediaStore('(prefers-reduced-motion: reduce)');

export const usePrefersDark = () => useSyncExternalStore(darkQuery.subscribe, darkQuery.get);
export const usePrefersReducedMotion = () =>
  useSyncExternalStore(reducedMotionQuery.subscribe, reducedMotionQuery.get);

export function useApplyTheme(setting: Theme): ResolvedTheme {
  const theme = resolveTheme(setting, usePrefersDark());
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', THEME_COLORS[theme]);
  }, [theme]);
  return theme;
}
