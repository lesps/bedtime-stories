import { Link, useParams } from 'react-router';
import { useHiddenVersions } from '../app/useVisibleStories';
import { LengthFilteredList } from '../components/LengthFilteredList';
import { StoryList } from '../components/StoryRow';
import { useIndex } from '../data/IndexProvider';
import { hiddenInCollection, visibleInCollection } from '../domain/navigation';
import { useSettings } from '../storage/StoreProvider';
import { NotFoundPage } from './NotFoundPage';

export function CollectionPage() {
  const { collectionId = '' } = useParams();
  const { stories, collectionsById } = useIndex();
  const settings = useSettings();
  const hidden = useHiddenVersions();
  const collection = collectionsById.get(collectionId);
  if (!collection) return <NotFoundPage />;
  const list = visibleInCollection(stories, collectionId, settings, hidden);
  const others = hiddenInCollection(stories, collectionId, settings, hidden);
  const othersLabel = settings.showOriginals ? 'Retellings for young readers' : 'Original texts';
  return (
    <div className="page">
      <Link to="/" className="back-link">
        ‹ Library
      </Link>
      <h1 className="page-title">{collection.title}</h1>
      <p className="muted">
        {collection.author}
        {collection.contributor && <> · {collection.contributor}</>}
        {collection.firstPublished && <> · {collection.firstPublished}</>}
      </p>
      {list.length > 0 && (
        <LengthFilteredList entries={list} label={`Stories in ${collection.title}`} />
      )}
      {others.length > 0 && (
        <section aria-labelledby="others-h" className="other-versions">
          <h2 id="others-h">{othersLabel}</h2>
          <p className="muted">
            {settings.showOriginals
              ? 'Listed in the library as their original texts.'
              : 'Listed in the library as their retellings for young readers.'}
          </p>
          <StoryList entries={others} label={othersLabel} />
        </section>
      )}
    </div>
  );
}
