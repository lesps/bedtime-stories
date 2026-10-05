import { vi } from 'vitest';

type Cb = (entries: Partial<IntersectionObserverEntry>[]) => void;

/** Installs a controllable IntersectionObserver. Call `show(indices)` to mark blocks visible. */
export function installFakeIO() {
  const observers: { cb: Cb; els: Set<Element> }[] = [];
  class FakeIO {
    els = new Set<Element>();
    constructor(public cb: Cb) {
      observers.push(this);
    }
    observe(el: Element) {
      this.els.add(el);
    }
    unobserve(el: Element) {
      this.els.delete(el);
    }
    disconnect() {
      this.els.clear();
    }
    takeRecords() {
      return [];
    }
  }
  vi.stubGlobal('IntersectionObserver', FakeIO);
  return {
    /** Sets exactly these block indices as visible. */
    show(indices: number[]) {
      for (const o of observers) {
        const entries = [...o.els].map((target) => ({
          target,
          isIntersecting: indices.includes(Number((target as HTMLElement).dataset.block)),
        }));
        if (entries.length) o.cb(entries);
      }
    },
  };
}
