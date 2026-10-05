import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

if (typeof window !== 'undefined') window.scrollTo = () => {};

afterEach(() => {
  if (typeof window === 'undefined') return;
  cleanup();
  localStorage.clear();
});
