import { useState } from 'react';
import type { Highlight } from '../storage/store';

/** Story note plus every highlight in reading order; set-aside ones listed separately. */
export function NotesPanel({
  storyNote,
  highlights,
  detached,
  onSaveStoryNote,
  onJump,
  onClose,
}: {
  storyNote: string;
  highlights: Highlight[];
  detached: Highlight[];
  onSaveStoryNote: (text: string) => void;
  onJump: (h: Highlight) => void;
  onClose: () => void;
}) {
  const [text, setText] = useState(storyNote);
  const save = () => text !== storyNote && onSaveStoryNote(text);
  const close = () => {
    save();
    onClose();
  };
  return (
    <div className="sheet-backdrop" onClick={close}>
      <div
        className="sheet notes-panel"
        role="dialog"
        aria-modal="true"
        aria-label="Notes"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => e.key === 'Escape' && close()}
      >
        <div className="row sheet-head">
          <h2>Notes</h2>
          <button type="button" className="btn ghost" onClick={close}>
            Close
          </button>
        </div>
        <label className="field">
          <span>Note on this story</span>
          <textarea
            rows={3}
            value={text}
            placeholder="Who loved it, what you talked about…"
            onChange={(e) => setText(e.target.value)}
            onBlur={save}
          />
        </label>
        {highlights.length === 0 && detached.length === 0 && (
          <p className="muted">Select any words in the story to highlight them or add a note.</p>
        )}
        {highlights.length > 0 && (
          <ul className="hl-list">
            {highlights.map((h) => (
              <li key={h.id}>
                <button type="button" className="hl-item" onClick={() => onJump(h)}>
                  <span className="hl-quote" data-color={h.color}>
                    {h.quote}
                  </span>
                  {h.note && <span className="hl-note">{h.note}</span>}
                </button>
              </li>
            ))}
          </ul>
        )}
        {detached.length > 0 && (
          <>
            <h3 className="filter-h">Couldn’t find these in the text</h3>
            <p className="muted hint">The story’s wording may have changed since you saved them.</p>
            <ul className="hl-list">
              {detached.map((h) => (
                <li key={h.id} className="hl-item detached">
                  <span className="hl-quote">{h.quote}</span>
                  {h.note && <span className="hl-note">{h.note}</span>}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
