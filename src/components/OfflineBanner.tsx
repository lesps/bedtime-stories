import { useOnline } from '../app/useOnline';

export function OfflineBanner() {
  if (useOnline()) return null;
  return (
    <div className="offline-banner" role="status">
      You’re offline. Saved stories still work.
    </div>
  );
}
