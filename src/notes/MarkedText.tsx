import type { KeyboardEvent } from 'react';
import { segments } from '../domain/annotations';
import type { HighlightColor } from '../storage/store';

export type Mark = {
  id: string;
  start: number;
  end: number;
  color: HighlightColor;
  hasNote: boolean;
};

/** Text with highlights rendered as tappable <mark>s. Adds no characters, so offsets stay valid. */
export function MarkedText({
  text,
  marks,
  onMark,
}: {
  text: string;
  marks?: Mark[];
  onMark?: (id: string) => void;
}) {
  if (!marks?.length) return <>{text}</>;
  const byId = new Map(marks.map((m) => [m.id, m]));
  return (
    <>
      {segments(text, marks).map((s, i) => {
        const m = s.id ? byId.get(s.id) : undefined;
        if (!m) return s.text;
        const open = () => onMark?.(m.id);
        return (
          <mark
            key={i}
            className="hl"
            data-color={m.color}
            data-note={m.hasNote || undefined}
            role="button"
            tabIndex={0}
            aria-label={`Highlight: ${s.text}${m.hasNote ? ', has a note' : ''}`}
            onClick={open}
            onKeyDown={(e: KeyboardEvent) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                open();
              }
            }}
          >
            {s.text}
          </mark>
        );
      })}
    </>
  );
}
