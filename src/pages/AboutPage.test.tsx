import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { renderApp } from '../test/renderApp';

describe('AboutPage', () => {
  it('credits each collection with a source link', async () => {
    renderApp('/about');
    expect(await screen.findByText('The Aesop for Children')).toBeInTheDocument();
    expect(
      screen.getAllByRole('link', { name: 'Source text' }).map((a) => a.getAttribute('href')),
    ).toEqual([
      'https://example.org/aesop',
      'https://example.org/grimm',
      'https://example.org/hunt',
    ]);
  });
});
