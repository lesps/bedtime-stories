import { useIndex } from '../data/IndexProvider';

export function AboutPage() {
  const { collections } = useIndex();
  return (
    <div className="page prose">
      <h1 className="page-title">About</h1>
      <p>
        Storybook is a quiet reader for public-domain children’s stories. Everything you do —
        favorites, reading position, settings — stays on this device.
      </p>
      <p>
        Some stories reflect the attitudes of their time. Stories with mature themes are hidden by
        default and can be shown in Settings. Those flags are an editorial first pass, not an
        exhaustive review.
      </p>
      <h2>Collections</h2>
      <ul className="credits">
        {collections.map((c) => (
          <li key={c.id}>
            <strong>{c.title}</strong>
            <br />
            {c.author}
            {c.contributor && <>; {c.contributor}</>}
            {c.firstPublished && <> ({c.firstPublished})</>}
            <br />
            <span className="muted">{c.license}. </span>
            <a href={c.source} rel="noopener noreferrer" target="_blank">
              Source text
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
