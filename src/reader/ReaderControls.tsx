import { useId, useState } from 'react';
import { FONT_SIZES, THEMES, type Theme } from '../storage/store';
import { useSettings, useStore } from '../storage/StoreProvider';

const THEME_LABELS: Record<Theme, string> = {
  system: 'Auto',
  light: 'Light',
  sepia: 'Sepia',
  dark: 'Dark',
};

export function ThemePicker() {
  const store = useStore();
  const { theme } = useSettings();
  return (
    <div className="chips" role="radiogroup" aria-label="Theme">
      {THEMES.map((t) => (
        <button
          key={t}
          type="button"
          role="radio"
          aria-checked={theme === t}
          className="chip"
          data-swatch={t}
          onClick={() => store.updateSettings({ theme: t })}
        >
          {THEME_LABELS[t]}
        </button>
      ))}
    </div>
  );
}

export function TypeControls() {
  const store = useStore();
  const { fontSize, lineHeight } = useSettings();
  return (
    <>
      <div className="row" role="group" aria-label="Text size">
        <button
          type="button"
          className="btn"
          aria-label="Smaller text"
          disabled={fontSize === 0}
          onClick={() => store.updateSettings({ fontSize: fontSize - 1 })}
        >
          A−
        </button>
        <span className="muted" aria-live="polite">
          Size {fontSize + 1} of {FONT_SIZES.length}
        </span>
        <button
          type="button"
          className="btn"
          aria-label="Larger text"
          disabled={fontSize === FONT_SIZES.length - 1}
          onClick={() => store.updateSettings({ fontSize: fontSize + 1 })}
        >
          A+
        </button>
      </div>
      <label className="toggle">
        <input
          type="checkbox"
          checked={lineHeight === 'relaxed'}
          onChange={(e) =>
            store.updateSettings({ lineHeight: e.target.checked ? 'relaxed' : 'normal' })
          }
        />
        Relaxed line spacing
      </label>
    </>
  );
}

export function ReaderControls() {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="reader-controls">
      <button
        type="button"
        className="icon-btn"
        aria-expanded={open}
        aria-controls={id}
        aria-label="Reading settings"
        onClick={() => setOpen(!open)}
      >
        <span aria-hidden="true" className="aa">
          Aa
        </span>
      </button>
      {open && (
        <div id={id} className="panel">
          <ThemePicker />
          <TypeControls />
        </div>
      )}
    </div>
  );
}
