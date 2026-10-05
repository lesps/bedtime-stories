import { useMemo } from 'react';
import { useIndex } from '../data/IndexProvider';
import { useSettings } from '../storage/StoreProvider';
import { isVisible } from '../domain/visibility';

export function useVisibleStories() {
  const { stories } = useIndex();
  const { showMature, showExcluded } = useSettings();
  return useMemo(
    () => stories.filter((s) => isVisible(s, { showMature, showExcluded })),
    [stories, showMature, showExcluded],
  );
}
