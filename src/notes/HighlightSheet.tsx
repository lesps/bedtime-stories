import { useEffect, useRef, useState } from 'react';
import { useDialog } from '../components/useDialog';
import { HIGHLIGHT_COLORS, type Highlight, type HighlightColor } from '../storage/store';

const LABEL: Record<HighlightColor, string> = {
  yellow: 'Yellow',
  green: 'Green',
  blue: 'Blue',
  pink: 'Pink',
};

/** Bottom sheet for one highlight: colour, note, delete. The note saves on Done or close. */
export function HighlightSheet({
  highlight,
  focusNote,
  onColor,
  onSaveNote,
  onDelete,
  onClose,
}: {
  highlight: Highlight;
  focusNote?: boolean;
  onColor: (c: HighlightColor) => void;
  onSaveNote: (note: string) => void;
  onDelete: () => void;
  onClose: () => void;
}) {
  const [note, setNote] = useState(highlight.note ?? '');
  const area = useRef<HTMLTextAreaElement>(null);
  const done = () => {
    if (note !== (highlight.note ?? '')) onSaveNote(note);
    onClose();
  };
  const dialog = useDialog<HTMLDivElement>(done);
  useEffect(() => {
    if (focusNote) area.current?.focus();
  }, [focusNote]);
  return (
    <div className="sheet-backdrop" onClick={done}>
      <div
        ref={dialog}
        tabIndex={-1}
        className="sheet"
        role="dialog"
        aria-modal="true"
        aria-label={`Highlight: ${highlight.quote}`}
        onClick={(e) => e.stopPropagation()}
      >
        <blockquote className="sheet-quote" data-color={highlight.color}>
          {highlight.quote}
        </blockquote>
        <div className="row" role="radiogroup" aria-label="Colour">
          {HIGHLIGHT_COLORS.map((c) => (
            <button
              key={c}
              type="button"
              role="radio"
              aria-checked={highlight.color === c}
              aria-label={LABEL[c]}
              className="swatch"
              data-color={c}
              onClick={() => onColor(c)}
            />
          ))}
        </div>
        <label className="field">
          <span>Note</span>
          <textarea
            ref={area}
            rows={3}
            value={note}
            placeholder="What did you notice? What did they say?"
            onChange={(e) => setNote(e.target.value)}
          />
        </label>
        <div className="row sheet-actions">
          <button type="button" className="btn primary" onClick={done}>
            Done
          </button>
          <button type="button" className="btn ghost" onClick={onDelete}>
            Delete highlight
          </button>
        </div>
      </div>
    </div>
  );
}
