import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { HighlightToolbar, toolbarPosition } from './HighlightToolbar';

const rect = (top: number, bottom: number, left = 100, width = 80) =>
  ({
    top,
    bottom,
    left,
    width,
    height: bottom - top,
    right: left + width,
    x: left,
    y: top,
  }) as DOMRect;

describe('toolbarPosition', () => {
  const vw = 412;
  const vh = 900;

  it('sits below the selection, clear of selection handles', () => {
    expect(toolbarPosition(rect(200, 220), vw, vh)).toMatchObject({ top: 260 });
  });

  it('flips above the selection when there is no room above the tab bar', () => {
    const p = toolbarPosition(rect(780, 800), vw, vh);
    expect(p.top).toBeLessThan(780);
    expect(p.top + 52).toBeLessThanOrEqual(780);
  });

  it('stays within the screen horizontally', () => {
    expect(toolbarPosition(rect(200, 220, 380, 30), vw, vh).left).toBeLessThanOrEqual(vw - 8 - 300);
    expect(toolbarPosition(rect(200, 220, 0, 10), vw, vh).left).toBeGreaterThanOrEqual(8);
  });

  it('renders the four colours and Add note', () => {
    render(
      <HighlightToolbar
        selection={{ block: 0, start: 0, end: 1, quote: 'a', rect: rect(200, 220) }}
        onColor={() => {}}
        onNote={() => {}}
      />,
    );
    expect(screen.getAllByRole('button')).toHaveLength(5);
  });
});
