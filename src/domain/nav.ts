export type Section = 'library' | 'surprise' | 'reading' | 'favorites' | 'settings';

export const TAB_ROOT: Record<Section, string> = {
  library: '/',
  surprise: '/surprise',
  reading: '/reading',
  favorites: '/favorites',
  settings: '/settings',
};

/** Which tab a route belongs to. Every story page is "reading": opening a story makes it the open book. */
export function sectionOf(pathname: string): Section | null {
  if (pathname === '/' || pathname.startsWith('/c/') || pathname.startsWith('/tags/'))
    return 'library';
  if (pathname === '/reading' || pathname.startsWith('/s/')) return 'reading';
  if (pathname === '/surprise') return 'surprise';
  if (pathname === '/favorites') return 'favorites';
  if (pathname === '/settings' || pathname === '/about') return 'settings';
  return null;
}

export type TabAction =
  | { type: 'navigate'; to: string }
  | { type: 'scrollTop' }
  | { type: 'reset' }
  | { type: 'closeBook'; storyId: string }
  | { type: 'none' };

/**
 * What tapping a tab does, following the platform convention: another tab → go there; the current
 * tab from deeper inside it → back to its main screen; on the main screen → scroll to top, then
 * (Library only) reset search and filters. In a story, tapping Reading closes the book.
 */
export function tabTap(tab: Section, pathname: string, scrolled: boolean): TabAction {
  if (sectionOf(pathname) !== tab) return { type: 'navigate', to: TAB_ROOT[tab] };
  if (pathname.startsWith('/s/')) return { type: 'closeBook', storyId: pathname.slice(3) };
  if (pathname !== TAB_ROOT[tab]) return { type: 'navigate', to: TAB_ROOT[tab] };
  if (scrolled) return { type: 'scrollTop' };
  return tab === 'library' ? { type: 'reset' } : { type: 'none' };
}
