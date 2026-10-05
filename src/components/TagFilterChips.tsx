import type { TagDef } from '../data/types';
import type { TagFilter } from '../domain/picker';

type State = 'any' | 'included' | 'excluded';
const next: Record<State, State> = { any: 'included', included: 'excluded', excluded: 'any' };

const stateOf = (f: TagFilter, id: string): State =>
  f.include.includes(id) ? 'included' : f.exclude.includes(id) ? 'excluded' : 'any';

/** Tri-state chips: tap once to include, twice to exclude, three times to clear. */
export function TagFilterChips({
  label,
  defs,
  value,
  onChange,
}: {
  label: string;
  defs: TagDef[];
  value: TagFilter;
  onChange: (f: TagFilter) => void;
}) {
  const cycle = (id: string) => {
    const s = next[stateOf(value, id)];
    const include = value.include.filter((t) => t !== id);
    const exclude = value.exclude.filter((t) => t !== id);
    if (s === 'included') include.push(id);
    if (s === 'excluded') exclude.push(id);
    onChange({ include, exclude });
  };
  return (
    <div className="chips tri" role="group" aria-label={label}>
      {defs.map((d) => {
        const s = stateOf(value, d.id);
        return (
          <button
            key={d.id}
            type="button"
            className="chip"
            data-state={s}
            aria-label={`${d.label}: ${s}`}
            onClick={() => cycle(d.id)}
          >
            <span aria-hidden="true" className="tri-mark">
              {s === 'included' ? '✓' : s === 'excluded' ? '✕' : ''}
            </span>
            {d.label}
          </button>
        );
      })}
    </div>
  );
}
