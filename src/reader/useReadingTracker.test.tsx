import { act, render } from '@testing-library/react';
import { useState } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { installFakeIO } from '../test/fakeIntersectionObserver';
import { useReadingTracker } from './useReadingTracker';

function Harness({ onTop, onFinal }: { onTop: (i: number) => void; onFinal: () => void }) {
  const [el, setEl] = useState<HTMLElement | null>(null);
  useReadingTracker(el, 4, onTop, onFinal, 100);
  return (
    <div ref={setEl}>
      {[0, 1, 2, 3].map((i) => (
        <p key={i} data-block={i} />
      ))}
    </div>
  );
}

describe('useReadingTracker', () => {
  let io: ReturnType<typeof installFakeIO>;
  beforeEach(() => {
    vi.useFakeTimers();
    io = installFakeIO();
  });

  it('reports the topmost visible block, throttled', () => {
    const onTop = vi.fn();
    render(<Harness onTop={onTop} onFinal={() => {}} />);
    act(() => {
      io.show([0, 1]);
      io.show([1, 2]);
    });
    expect(onTop).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(100));
    expect(onTop).toHaveBeenCalledTimes(1);
    expect(onTop).toHaveBeenCalledWith(1);
  });

  it('fires onFinal once when the last block appears', () => {
    const onFinal = vi.fn();
    render(<Harness onTop={() => {}} onFinal={onFinal} />);
    act(() => io.show([2, 3]));
    act(() => io.show([3]));
    expect(onFinal).toHaveBeenCalledTimes(1);
  });
});
