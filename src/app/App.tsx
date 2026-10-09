import { HashRouter, Outlet, Route, Routes, useLocation } from 'react-router';
import { OfflineBanner } from '../components/OfflineBanner';
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
import { StoreProvider, useSettings } from '../storage/StoreProvider';
import type { Store } from '../storage/store';
import { TabBar } from './TabBar';
import { useApplyTheme } from './theme';
import { useScrollMemory } from './useScrollMemory';

function Layout() {
  useApplyTheme(useSettings().theme);
  useScrollMemory();
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
      <TabBar />
    </>
  );
}

/** Remounts the library when the Library tab asks for a reset (fresh `state.reset`). */
function LibraryRoute() {
  const { state } = useLocation();
  const reset = (state as { reset?: number } | null)?.reset;
  return <LibraryPage key={reset ?? 0} />;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LibraryRoute />} />
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
