import { fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { FULL_RANGE, LENGTH_STOPS, type LengthRange } from '../domain/length';
import { LengthSlider } from './LengthSlider';

const idx = (m: number) => String(LENGTH_STOPS.indexOf(m as (typeof LENGTH_STOPS)[number]));

function Harness({ initial, spy }: { initial: LengthRange; spy?: (r: LengthRange) => void }) {
  const [r, setR] = useState(initial);
  return (
    <LengthSlider
      value={r}
      onChange={(n) => {
        spy?.(n);
        setR(n);
      }}
    />
  );
}

describe('LengthSlider', () => {
  it('exposes two labelled sliders with human value text', () => {
    render(<Harness initial={{ min: 1, max: 5 }} />);
    expect(screen.getByRole('slider', { name: 'Shortest' })).toHaveAttribute(
      'aria-valuetext',
      '1 min',
    );
    expect(screen.getByRole('slider', { name: 'Longest' })).toHaveAttribute(
      'aria-valuetext',
      '5 min',
    );
    expect(screen.getByRole('status')).toHaveTextContent('Up to 5 min');
  });

  it('selects only medium stories (6–15 min)', () => {
    const spy = vi.fn();
    render(<Harness initial={{ min: 1, max: 5 }} spy={spy} />);
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), {
      target: { value: idx(15) },
    });
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), {
      target: { value: idx(7) },
    });
    expect(spy).toHaveBeenLastCalledWith({ min: 7, max: 15 });
    expect(screen.getByRole('status')).toHaveTextContent('7–15 min');
  });

  it('selects only long stories with no upper bound at 60+', () => {
    const spy = vi.fn();
    render(<Harness initial={{ min: 1, max: 5 }} spy={spy} />);
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), {
      target: { value: idx(60) },
    });
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), {
      target: { value: idx(15) },
    });
    expect(spy).toHaveBeenLastCalledWith({ min: 15, max: null });
    expect(screen.getByRole('slider', { name: 'Longest' })).toHaveAttribute(
      'aria-valuetext',
      '60+ min',
    );
  });

  it('never lets the handles cross', () => {
    const spy = vi.fn();
    render(<Harness initial={{ min: 3, max: 10 }} spy={spy} />);
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), {
      target: { value: idx(30) },
    });
    expect(spy).toHaveBeenLastCalledWith({ min: 10, max: 10 });
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), {
      target: { value: idx(2) },
    });
    expect(spy).toHaveBeenLastCalledWith({ min: 10, max: 10 });
  });

  it('reads "Any length" across the full range', () => {
    render(<Harness initial={FULL_RANGE} />);
    expect(screen.getByRole('status')).toHaveTextContent('Any length');
  });

  it('raises the Shortest handle when both handles meet at the top, so it can still move', () => {
    render(<Harness initial={{ min: 60, max: null }} />);
    expect(screen.getByRole('slider', { name: 'Shortest' })).toHaveClass('on-top');
    render(<Harness initial={{ min: 1, max: 1 }} />);
    expect(screen.getAllByRole('slider', { name: 'Shortest' })[1]).not.toHaveClass('on-top');
  });
});
