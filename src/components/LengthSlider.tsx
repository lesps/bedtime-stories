import { useId } from 'react';
import { LENGTH_STOPS, formatRange, stopLabel, type LengthRange } from '../domain/length';

const LAST = LENGTH_STOPS.length - 1;
const TICKS = [1, 5, 15, 30, 60];
const indexOf = (m: number | null) => {
  if (m == null) return LAST;
  const i = LENGTH_STOPS.findIndex((s) => s >= m);
  return i === -1 ? LAST : i;
};

/** Two-handled length picker over stepped minute stops. */
export function LengthSlider({
  value,
  onChange,
  label = 'Length',
}: {
  value: LengthRange;
  onChange: (r: LengthRange) => void;
  label?: string;
}) {
  const id = useId();
  const lo = indexOf(value.min);
  const hi = indexOf(value.max);
  const emit = (a: number, b: number) =>
    onChange({ min: LENGTH_STOPS[a]!, max: b === LAST ? null : LENGTH_STOPS[b]! });

  return (
    <fieldset className="length-slider">
      <legend id={`${id}-l`}>{label}</legend>
      <output role="status" aria-live="polite" className="length-value">
        {formatRange(value)}
      </output>
      <div
        className="range"
        style={{ '--lo': lo / LAST, '--hi': hi / LAST } as React.CSSProperties}
      >
        <input
          type="range"
          min={0}
          max={LAST}
          step={1}
          value={lo}
          aria-label="Shortest"
          // When the handles meet in the upper half, Longest (painted on top) can't move left past
          // Shortest, so lift Shortest above it.
          className={lo === hi && lo > LAST / 2 ? 'on-top' : undefined}
          aria-valuetext={stopLabel(LENGTH_STOPS[lo]!)}
          onChange={(e) => emit(Math.min(Number(e.target.value), hi), hi)}
        />
        <input
          type="range"
          min={0}
          max={LAST}
          step={1}
          value={hi}
          aria-label="Longest"
          aria-valuetext={stopLabel(LENGTH_STOPS[hi]!)}
          onChange={(e) => emit(lo, Math.max(Number(e.target.value), lo))}
        />
      </div>
      <div className="range-ticks" aria-hidden="true">
        {TICKS.map((m) => (
          <span key={m} style={{ left: `${(indexOf(m) / LAST) * 100}%` }}>
            {m === 60 ? '60+' : m}
          </span>
        ))}
      </div>
    </fieldset>
  );
}
