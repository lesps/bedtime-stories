import type { MouseEvent, ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router';
import { BookIcon, GearIcon, HeartIcon, OpenBookIcon, SparkleIcon } from '../components/icons';
import { TAB_ROOT, sectionOf, tabTap, type Section } from '../domain/nav';
import { useStore } from '../storage/StoreProvider';
import { usePrefersReducedMotion } from './theme';

const TABS: { id: Section; label: string; icon: ReactNode }[] = [
  { id: 'library', label: 'Library', icon: <BookIcon /> },
  { id: 'surprise', label: 'Surprise', icon: <SparkleIcon /> },
  { id: 'reading', label: 'Reading', icon: <OpenBookIcon /> },
  { id: 'favorites', label: 'Favorites', icon: <HeartIcon filled={false} /> },
  { id: 'settings', label: 'Settings', icon: <GearIcon /> },
];

/**
 * Bottom tabs. The current tab follows the section you're in, and tapping it again does the
 * platform-standard thing (see `tabTap`): back to its main screen, scroll to top, or reset; in a
 * story, tapping Reading closes the book.
 */
export function TabBar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const store = useStore();
  const reducedMotion = usePrefersReducedMotion();
  const current = sectionOf(pathname);

  const onTap = (tab: Section) => (e: MouseEvent) => {
    e.preventDefault();
    const action = tabTap(tab, pathname, window.scrollY > 0);
    switch (action.type) {
      case 'navigate':
        navigate(action.to);
        break;
      case 'closeBook':
        store.closeStory(action.storyId);
        navigate('/reading');
        break;
      case 'scrollTop':
        window.scrollTo({ top: 0, behavior: reducedMotion ? 'auto' : 'smooth' });
        break;
      case 'reset':
        // A fresh key remounts the library, clearing its search and filters.
        navigate('/', { replace: true, state: { reset: Date.now() } });
        break;
    }
  };

  return (
    <nav className="tabbar" aria-label="Main">
      <span className="tabbar-brand" aria-hidden="true">
        Storybook
      </span>
      {TABS.map((t) => (
        <Link
          key={t.id}
          to={TAB_ROOT[t.id]}
          className={current === t.id ? 'active' : undefined}
          aria-current={current === t.id ? 'page' : undefined}
          onClick={onTap(t.id)}
        >
          {t.icon}
          <span>{t.label}</span>
        </Link>
      ))}
    </nav>
  );
}
