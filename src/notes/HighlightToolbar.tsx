import type { PointerEvent } from 'react';
import { HIGHLIGHT_COLORS, type HighlightColor } from '../storage/store';
import type { SelectionInfo } from './selection';

// Clears Android's selection handles, which hang ~25px below the text.
const GAP = 40;
const WIDTH = 300;
const HEIGHT = 52;
/** Space the fixed tab bar takes at the bottom of the screen. */
const TAB_BAR = 90;

/**
 * Below the selection, where it can't collide with the phone's own copy/share callout (drawn
 * above). If there's no room above the tab bar, flip above the selection instead.
 */
export function toolbarPosition(r: DOMRect, vw: number, vh: number) {
  const below = r.bottom + GAP;
  const top = below + HEIGHT <= vh - TAB_BAR ? below : Math.max(8, r.top - GAP - HEIGHT);
  const left = Math.max(8, Math.min(vw - WIDTH - 8, r.left + r.width / 2 - WIDTH / 2));
  return { top, left };
}

export function HighlightToolbar({
  selection,
  onColor,
  onNote,
}: {
  selection: SelectionInfo;
  onColor: (c: HighlightColor) => void;
  onNote: () => void;
}) {
  const r = selection.rect;
  const style =
    r && r.width + r.height > 0
      ? toolbarPosition(r, window.innerWidth, window.innerHeight)
      : { bottom: TAB_BAR + 8, left: Math.max(8, window.innerWidth / 2 - WIDTH / 2) };
  // Keep the text selection alive while a button is pressed.
  const keep = (e: PointerEvent) => e.preventDefault();
  return (
    <div className="hl-toolbar" role="toolbar" aria-label="Highlight" style={style}>
      {HIGHLIGHT_COLORS.map((c) => (
        <button
          key={c}
          type="button"
          className="swatch"
          data-color={c}
          aria-label={`Highlight ${c}`}
          onPointerDown={keep}
          onClick={() => onColor(c)}
        />
      ))}
      <button type="button" className="btn ghost note-btn" onPointerDown={keep} onClick={onNote}>
        Add note
      </button>
    </div>
  );
}
