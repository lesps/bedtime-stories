import { useMemo } from 'react';
import { useIndex } from '../data/IndexProvider';
import { useSettings } from '../storage/StoreProvider';
import { isVisible } from '../domain/visibility';
import { hiddenVersions } from '../domain/versions';

/** Stories that content settings allow: for lists the reader made (favorites, history). */
export function useVisibleStories() {
  const { stories } = useIndex();
  const { showMature, showExcluded } = useSettings();
  return useMemo(
    () => stories.filter((s) => isVisible(s, { showMature, showExcluded })),
    [stories, showMature, showExcluded],
  );
}

/** Versions of retold myths left out of listings, under the current settings. */
export function useHiddenVersions() {
  const { stories } = useIndex();
  const { showMature, showExcluded, showOriginals } = useSettings();
  return useMemo(
    () => hiddenVersions(stories, { showMature, showExcluded, showOriginals }),
    [stories, showMature, showExcluded, showOriginals],
  );
}

/** Visible stories with one version of each retold myth: for browsing, search and picking. */
export function useListedStories() {
  const visible = useVisibleStories();
  const hidden = useHiddenVersions();
  return useMemo(() => visible.filter((s) => !hidden.has(s.id)), [visible, hidden]);
}
