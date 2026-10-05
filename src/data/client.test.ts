import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DataError, compendiumUrl, loadIndex, loadStory, resetDataCache } from './client';

const index = {
  schemaVersion: 1,
  collections: [
    {
      id: 'aesop',
      title: 'Aesop',
      author: 'Aesop',
      contributor: null,
      firstPublished: 1919,
      source: 'https://example.org/1',
      license: 'Public domain in the USA',
      storyCount: 1,
      language: 'en',
      originalLanguage: 'en',
    },
  ],
  stories: [
    {
      id: 'aesop--a',
      collectionId: 'aesop',
      order: 1,
      title: 'A',
      wordCount: 10,
      readingMinutes: 1,
      excluded: false,
      flags: [],
      hasImages: false,
    },
  ],
};
const story = {
  id: 'aesop--a',
  collectionId: 'aesop',
  order: 1,
  title: 'A',
  wordCount: 10,
  readingMinutes: 1,
  excluded: false,
  flags: [],
  origin: null,
  moral: null,
  blocks: [{ type: 'p', text: 'Once.' }],
};

const ok = (body: unknown) => new Response(JSON.stringify(body), { status: 200 });
let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  resetDataCache();
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
});

describe('loadIndex', () => {
  it('fetches and validates once, then serves from cache', async () => {
    fetchMock.mockResolvedValue(ok(index));
    const a = await loadIndex();
    const b = await loadIndex();
    expect(a).toBe(b);
    expect(a.stories[0]?.id).toBe('aesop--a');
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(compendiumUrl('index.json'));
  });

  it('typesets story titles in the index', async () => {
    fetchMock.mockResolvedValue(
      ok({ ...index, stories: [{ ...index.stories[0], title: "The Lion's Share" }] }),
    );
    expect((await loadIndex()).stories[0]?.title).toBe('The Lion’s Share');
  });

  it('throws an invalid DataError on schema mismatch', async () => {
    fetchMock.mockResolvedValue(ok({ ...index, schemaVersion: 2 }));
    await expect(loadIndex()).rejects.toMatchObject({ name: 'DataError', kind: 'invalid' });
  });

  it('throws an http DataError on non-2xx and retries on next call', async () => {
    fetchMock.mockResolvedValueOnce(new Response('', { status: 500 }));
    await expect(loadIndex()).rejects.toMatchObject({ kind: 'http', status: 500 });
    fetchMock.mockResolvedValueOnce(ok(index));
    await expect(loadIndex()).resolves.toBeTruthy();
  });

  it('throws a network DataError when fetch rejects', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'));
    const err = await loadIndex().catch((e: unknown) => e);
    expect(err).toBeInstanceOf(DataError);
    expect(err).toMatchObject({ kind: 'network' });
  });
});

describe('loadStory', () => {
  it('memoizes by id', async () => {
    fetchMock.mockImplementation(async () => ok(story));
    const [a, b] = await Promise.all([loadStory('aesop--a'), loadStory('aesop--a')]);
    expect(a).toBe(b);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(compendiumUrl('stories/aesop--a.json'));
  });

  it('typesets ASCII quotes and dashes in titles and text, leaving the source data alone', async () => {
    fetchMock.mockResolvedValue(
      ok({
        ...story,
        title: "The Lion's Share",
        moral: 'Be "kind"--always.',
        blocks: [
          { type: 'p', text: '"Hello," he said.' },
          { type: 'image', src: "images/x's.jpg", alt: "the lion's den" },
        ],
      }),
    );
    const s = await loadStory('aesop--a');
    expect(s.title).toBe('The Lion’s Share');
    expect(s.moral).toBe('Be “kind”—always.');
    expect(s.blocks[0]).toEqual({ type: 'p', text: '“Hello,” he said.' });
    expect(s.blocks[1]).toEqual({ type: 'image', src: "images/x's.jpg", alt: 'the lion’s den' });
  });

  it('rejects unknown block types', async () => {
    fetchMock.mockResolvedValue(ok({ ...story, blocks: [{ type: 'table', text: '' }] }));
    await expect(loadStory('aesop--a')).rejects.toMatchObject({ kind: 'invalid' });
  });

  it('rejects ids that would escape the stories directory', async () => {
    await expect(loadStory('../index')).rejects.toMatchObject({ kind: 'invalid' });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
