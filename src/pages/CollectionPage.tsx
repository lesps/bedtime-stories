import { Link, useParams } from 'react-router';
import { StoryList } from '../components/StoryRow';
import { useIndex } from '../data/IndexProvider';
import { visibleInCollection } from '../domain/navigation';
import { useSettings } from '../storage/StoreProvider';
import { NotFoundPage } from './NotFoundPage';

export function CollectionPage() {
  const { collectionId = '' } = useParams();
  const { stories, collectionsById } = useIndex();
  const settings = useSettings();
  const collection = collectionsById.get(collectionId);
  if (!collection) return <NotFoundPage />;
  const list = visibleInCollection(stories, collectionId, settings);
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
      <StoryList entries={list} label={`Stories in ${collection.title}`} />
    </div>
  );
}
