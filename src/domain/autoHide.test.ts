import { describe, expect, it } from 'vitest';
import { autoHide, type AutoHide } from './autoHide';

const run = (ys: number[], start: AutoHide = { visible: true, anchor: 0 }) =>
  ys.reduce(autoHide, start).visible;

describe('autoHide', () => {
  it.each([
    ['stays visible near the top', [10, 40, 60], true],
    ['hides once scrolled down past the threshold', [100, 200, 300], false],
    ['ignores jitter while scrolling down', [300, 304, 306], false],
    ['shows again on a clear scroll up', [300, 600, 580], true],
    ['adds up small steps up', [300, 600, 597, 594, 591, 588, 585], true],
    ['ignores a tiny scroll up', [300, 600, 596], false],
    ['hides again after showing', [300, 600, 500, 520, 540], false],
    ['always shows back at the top', [300, 600, 20], true],
  ] as const)('%s', (_, ys, visible) => expect(run([...ys])).toBe(visible));
});
