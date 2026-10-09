import { Link, useParams } from 'react-router';
import { useVisibleStories } from '../app/useVisibleStories';
import { StoryList } from '../components/StoryRow';
import { useIndex } from '../data/IndexProvider';
import type { TagKind } from '../data/types';
import { NotFoundPage } from './NotFoundPage';

const KIND_LABEL: Record<TagKind, string> = { cultures: 'Cultures', themes: 'Themes' };
const isKind = (k: string | undefined): k is TagKind => k === 'cultures' || k === 'themes';

export function TagPage() {
  const { kind, tagId = '' } = useParams();
  const { tagDef, tagsOf } = useIndex();
  const visible = useVisibleStories();
  const def = isKind(kind) ? tagDef(kind, tagId) : undefined;
  if (!isKind(kind) || !def) return <NotFoundPage />;
  const list = visible
    .filter((s) => tagsOf(s.id)[kind].includes(tagId))
    .sort((a, b) => a.title.localeCompare(b.title));
  return (
    <div className="page">
      <Link to={`/?by=${kind}`} className="back-link">
        ‹ {KIND_LABEL[kind]}
      </Link>
      <h1 className="page-title">{def.label}</h1>
      <p className="muted">
        {list.length} {list.length === 1 ? 'story' : 'stories'}
      </p>
      <StoryList entries={list} showCollection label={def.label} />
    </div>
  );
}
