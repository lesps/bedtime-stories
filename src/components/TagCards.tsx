import { Link } from 'react-router';
import { useVisibleStories } from '../app/useVisibleStories';
import { useIndex } from '../data/IndexProvider';
import type { TagKind } from '../data/types';

/** One card per tag with its visible-story count; tags with no visible stories are left out. */
export function TagCards({ kind }: { kind: TagKind }) {
  const { tags, tagsOf } = useIndex();
  const visible = useVisibleStories();
  const counts = new Map<string, number>();
  for (const s of visible)
    for (const t of tagsOf(s.id)[kind]) counts.set(t, (counts.get(t) ?? 0) + 1);
  const defs = tags[kind]
    .filter((d) => counts.get(d.id))
    .sort((a, b) => counts.get(b.id)! - counts.get(a.id)!);
  return (
    <ul className="collections tag-cards">
      {defs.map((d) => {
        const n = counts.get(d.id)!;
        return (
          <li key={d.id}>
            <Link to={`/tags/${kind}/${d.id}`} className="collection-card">
              <span className="collection-title">{d.label}</span>
              <span className="count">
                {n} {n === 1 ? 'story' : 'stories'}
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
