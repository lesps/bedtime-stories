import { Link } from 'react-router';

export function NotFoundPage() {
  return (
    <div className="page">
      <h1 className="page-title">Not found</h1>
      <p>That page or story isn’t here.</p>
      <Link to="/">Back to the library</Link>
    </div>
  );
}
