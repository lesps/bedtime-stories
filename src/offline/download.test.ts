import { beforeEach, describe, expect, it, vi } from 'vitest';
import { compendiumUrl } from '../data/client';
import { IMAGE_CACHE, STORY_CACHE, countCachedStories, downloadAll } from './download';

function fakeCaches() {
  const stores = new Map<string, Map<string, Response>>();
  const open = async (name: string) => {
    const m = stores.get(name) ?? new Map<string, Response>();
    stores.set(name, m);
    return {
      match: async (url: string) => m.get(url)?.clone(),
      put: async (url: string, res: Response) => void m.set(url, res),
      keys: async () => [...m.keys()].map((u) => new Request(new URL(u, 'http://x/'))),
    };
  };
  return { stores, api: { open } };
}

const story = (id: string, img?: string) => ({
  id,
  blocks: img ? [{ type: 'image', src: img, alt: '' }] : [{ type: 'p', text: 'x' }],
});

describe('downloadAll', () => {
  let caches: ReturnType<typeof fakeCaches>;
  let fetchMock: ReturnType<typeof vi.fn>;
  beforeEach(() => {
    caches = fakeCaches();
    vi.stubGlobal('caches', caches.api);
    fetchMock = vi.fn(async (url: string) =>
      url.includes('/images/')
        ? new Response('img')
        : new Response(
            JSON.stringify(
              story(
                url.split('/').pop()!.replace('.json', ''),
                url.includes('a--1') ? 'images/a/1.jpg' : undefined,
              ),
            ),
          ),
    );
    vi.stubGlobal('fetch', fetchMock);
  });

  it('caches every story and its images, reporting progress', async () => {
    const progress: number[] = [];
    const r = await downloadAll(['a--1', 'a--2', 'a--3'], (done, total) =>
      progress.push(done / total),
    );
    expect(r).toEqual({ stories: 3, images: 1, failed: 0 });
    expect(caches.stores.get(STORY_CACHE)?.size).toBe(3);
    expect([...caches.stores.get(IMAGE_CACHE)!.keys()]).toEqual([compendiumUrl('images/a/1.jpg')]);
    expect(progress.at(-1)).toBe(1);
    expect(await countCachedStories()).toBe(3);
  });

  it('can skip illustrations to save space', async () => {
    const r = await downloadAll(['a--1', 'a--2'], () => {}, { images: false });
    expect(r).toEqual({ stories: 2, images: 0, failed: 0 });
    expect(caches.stores.get(STORY_CACHE)?.size).toBe(2);
    expect(caches.stores.get(IMAGE_CACHE)?.size ?? 0).toBe(0);
  });

  it('skips stories already cached', async () => {
    await downloadAll(['a--2'], () => {});
    fetchMock.mockClear();
    await downloadAll(['a--2'], () => {});
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('counts failures without throwing', async () => {
    fetchMock.mockResolvedValueOnce(new Response('', { status: 404 }));
    const r = await downloadAll(['a--2', 'a--3'], () => {});
    expect(r.failed).toBe(1);
    expect(r.stories).toBe(1);
  });
});
