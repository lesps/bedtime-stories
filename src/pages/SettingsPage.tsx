import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { useIndex } from '../data/IndexProvider';
import { OFFLINE_MB, countCachedStories, downloadAll, offlineSupported } from '../offline/download';
import { ThemePicker, TypeControls } from '../reader/ReaderControls';
import { useSettings, useStore } from '../storage/StoreProvider';

export function SettingsPage() {
  const store = useStore();
  const { showMature, showExcluded } = useSettings();
  return (
    <div className="page">
      <h1 className="page-title">Settings</h1>

      <section aria-labelledby="look-h" className="card">
        <h2 id="look-h">Reading</h2>
        <p className="muted">“Auto” follows your phone: sepia by day, dark at night.</p>
        <ThemePicker />
        <TypeControls />
      </section>

      <section aria-labelledby="content-h" className="card">
        <h2 id="content-h">For grown-ups</h2>
        <label className="toggle">
          <input
            type="checkbox"
            checked={showMature}
            onChange={(e) => store.updateSettings({ showMature: e.target.checked })}
          />
          Show stories with mature themes
        </label>
        <label className="toggle">
          <input
            type="checkbox"
            checked={showExcluded}
            onChange={(e) => store.updateSettings({ showExcluded: e.target.checked })}
          />
          Show stories excluded for offensive language
        </label>
      </section>

      <OfflineSection />
      <ClearDataSection />

      <p className="footer-links">
        <Link to="/about">About &amp; credits</Link>
      </p>
    </div>
  );
}

function OfflineSection() {
  const { stories } = useIndex();
  const [cached, setCached] = useState<number | null>(null);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);
  const [message, setMessage] = useState('');
  const [withImages, setWithImages] = useState(true);
  const mb = OFFLINE_MB.stories + (withImages ? OFFLINE_MB.images : 0);

  useEffect(() => {
    countCachedStories().then(setCached, () => setCached(null));
  }, []);

  if (!offlineSupported()) return null;

  const run = async () => {
    setMessage('');
    setProgress({ done: 0, total: stories.length });
    const r = await downloadAll(
      stories.map((s) => s.id),
      (done, total) => setProgress({ done, total }),
      { images: withImages },
    );
    setProgress(null);
    setCached(await countCachedStories());
    setMessage(
      r.failed
        ? `Saved ${r.stories} stories; ${r.failed} couldn’t be downloaded. Try again when you have a better connection.`
        : withImages
          ? `All ${r.stories} stories and ${r.images} illustrations are saved for offline reading.`
          : `All ${r.stories} stories are saved for offline reading.`,
    );
  };

  return (
    <section aria-labelledby="offline-h" className="card">
      <h2 id="offline-h">Offline</h2>
      <p className="muted">
        Stories you open are saved automatically.{' '}
        {cached != null && `${cached} of ${stories.length} saved on this device.`}
      </p>
      <label className="toggle">
        <input
          type="checkbox"
          checked={withImages}
          disabled={progress !== null}
          onChange={(e) => setWithImages(e.target.checked)}
        />
        Include illustrations (about {OFFLINE_MB.images} MB)
      </label>
      <button type="button" className="btn" disabled={progress !== null} onClick={run}>
        Make all stories available offline (about {mb} MB)
      </button>
      {progress && (
        <div role="status">
          <progress value={progress.done} max={progress.total} aria-label="Download progress" />{' '}
          {progress.done} / {progress.total}
        </div>
      )}
      {message && <p role="status">{message}</p>}
    </section>
  );
}

function ClearDataSection() {
  const store = useStore();
  const [confirming, setConfirming] = useState(false);
  const [done, setDone] = useState(false);
  return (
    <section aria-labelledby="data-h" className="card">
      <h2 id="data-h">Reading data</h2>
      <p className="muted">
        Favorites, reading positions, and history are stored only on this device.
      </p>
      {confirming ? (
        <div className="row" role="group" aria-label="Confirm clearing reading data">
          <span>Clear favorites, positions, and history?</span>
          <button
            type="button"
            className="btn danger"
            onClick={() => {
              store.clearReadingData();
              setConfirming(false);
              setDone(true);
            }}
          >
            Yes, clear
          </button>
          <button type="button" className="btn" onClick={() => setConfirming(false)}>
            Cancel
          </button>
        </div>
      ) : (
        <button
          type="button"
          className="btn"
          onClick={() => {
            setDone(false);
            setConfirming(true);
          }}
        >
          Clear reading data
        </button>
      )}
      {done && <p role="status">Reading data cleared.</p>}
    </section>
  );
}
