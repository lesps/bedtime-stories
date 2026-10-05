import { describe, expect, it } from 'vitest';
import { collection } from '../test/fixtures';
import { collectionLabels } from './collectionLabel';

describe('collectionLabels', () => {
  it('disambiguates duplicate titles by the credited person’s surname', () => {
    const labels = collectionLabels([
      collection({
        id: 'oz',
        title: 'Japanese Fairy Tales',
        contributor: 'Compiled and translated by Yei Theodora Ozaki',
      }),
      collection({
        id: 'ja',
        title: 'Japanese Fairy Tales',
        contributor: 'Retold by Grace James, illustrated by Warwick Goble',
      }),
      collection({
        id: 'ae',
        title: 'The Aesop for Children',
        contributor: 'Illustrated by Milo Winter',
      }),
    ]);
    expect(labels.get('oz')).toBe('Japanese Fairy Tales (Ozaki)');
    expect(labels.get('ja')).toBe('Japanese Fairy Tales (James)');
    expect(labels.get('ae')).toBe('The Aesop for Children');
  });

  it('falls back to the id when there is no contributor', () => {
    const labels = collectionLabels([
      collection({ id: 'x-1', title: 'Tales', contributor: null }),
      collection({ id: 'x-2', title: 'Tales', contributor: null }),
    ]);
    expect([labels.get('x-1'), labels.get('x-2')]).toEqual(['Tales (x-1)', 'Tales (x-2)']);
  });
});
