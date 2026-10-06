import { useEffect } from 'react';
import { HashRouter, Link, NavLink, Outlet, Route, Routes, useLocation } from 'react-router';
import { OfflineBanner } from '../components/OfflineBanner';
import { BookIcon, GearIcon, HeartIcon, OpenBookIcon, SparkleIcon } from '../components/icons';
import { IndexProvider } from '../data/IndexProvider';
import { AboutPage } from '../pages/AboutPage';
import { CollectionPage } from '../pages/CollectionPage';
import { FavoritesPage } from '../pages/FavoritesPage';
import { LibraryPage } from '../pages/LibraryPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { ReadingPage } from '../pages/ReadingPage';
import { SettingsPage } from '../pages/SettingsPage';
import { SurprisePage } from '../pages/SurprisePage';
import { TagPage } from '../pages/TagPage';
import { ReaderRoute } from '../reader/ReaderPage';
import { StoreProvider, useAppState, useSettings } from '../storage/StoreProvider';
import type { Store } from '../storage/store';
import { useApplyTheme } from './theme';

function Layout() {
  useApplyTheme(useSettings().theme);
  const { pathname } = useLocation();
  const { openStoryId } = useAppState();
  // While reading the open story, the Reading tab is the current one.
  const readingActive =
    pathname === '/reading' || (!!openStoryId && pathname === `/s/${openStoryId}`);
  useEffect(() => window.scrollTo(0, 0), [pathname]);
  return (
    <>
      <a
        href="#main"
        className="skip-link"
        onClick={(e) => (e.preventDefault(), document.getElementById('main')?.focus())}
      >
        Skip to content
      </a>
      <OfflineBanner />
      <main id="main" tabIndex={-1}>
        <IndexProvider>
          <Outlet />
        </IndexProvider>
      </main>
      <nav className="tabbar" aria-label="Main">
        <NavLink to="/" end>
          <BookIcon />
          <span>Library</span>
        </NavLink>
        <NavLink to="/surprise">
          <SparkleIcon />
          <span>Surprise</span>
        </NavLink>
        <Link
          to="/reading"
          className={readingActive ? 'active' : undefined}
          aria-current={readingActive ? 'page' : undefined}
        >
          <OpenBookIcon />
          <span>Reading</span>
        </Link>
        <NavLink to="/favorites">
          <HeartIcon filled={false} />
          <span>Favorites</span>
        </NavLink>
        <NavLink to="/settings">
          <GearIcon />
          <span>Settings</span>
        </NavLink>
      </nav>
    </>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LibraryPage />} />
        <Route path="c/:collectionId" element={<CollectionPage />} />
        <Route path="tags/:kind/:tagId" element={<TagPage />} />
        <Route path="s/:storyId" element={<ReaderRoute />} />
        <Route path="reading" element={<ReadingPage />} />
        <Route path="favorites" element={<FavoritesPage />} />
        <Route path="surprise" element={<SurprisePage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export function App({ store }: { store?: Store }) {
  return (
    <StoreProvider store={store}>
      <HashRouter>
        <AppRoutes />
      </HashRouter>
    </StoreProvider>
  );
}
