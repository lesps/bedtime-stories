import { compendiumUrl } from '../data/client';

/** Must match the runtime cache names in vite.config.ts so the service worker serves these. */
export const STORY_CACHE = 'stories';
export const IMAGE_CACHE = 'images';

/** Approximate download sizes in MB; integrity.test.ts fails if these drift from the data. */
export const OFFLINE_MB = { stories: 5, images: 31 };

export const offlineSupported = () => typeof caches !== 'undefined';

export async function countCachedStories(): Promise<number> {
  if (!offlineSupported()) return 0;
  const keys = await (await caches.open(STORY_CACHE)).keys();
  return keys.filter((r) => r.url.includes('/compendium/stories/')).length;
}

async function cacheOne(cache: Cache, url: string): Promise<Response> {
  const hit = await cache.match(url);
  if (hit) return hit;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} returned ${res.status}`);
  await cache.put(url, res.clone());
  return res;
}

/** Fetches every story (and its illustrations) into the offline caches. */
export async function downloadAll(
  ids: string[],
  onProgress: (done: number, total: number) => void,
  { images: withImages = true, concurrency = 6 }: { images?: boolean; concurrency?: number } = {},
): Promise<{ stories: number; images: number; failed: number }> {
  const [storyCache, imageCache] = await Promise.all([
    caches.open(STORY_CACHE),
    caches.open(IMAGE_CACHE),
  ]);
  let done = 0;
  let images = 0;
  let failed = 0;
  const queue = [...ids];

  const worker = async () => {
    for (let id = queue.shift(); id; id = queue.shift()) {
      try {
        const res = await cacheOne(storyCache, compendiumUrl(`stories/${id}.json`));
        const { blocks } = (await res.json()) as { blocks: { type: string; src?: string }[] };
        for (const b of withImages ? blocks : []) {
          if (b.type !== 'image' || !b.src) continue;
          await cacheOne(imageCache, compendiumUrl(b.src));
          images++;
        }
      } catch {
        failed++;
      }
      onProgress(++done, ids.length);
    }
  };
  await Promise.all(Array.from({ length: concurrency }, worker));
  return { stories: ids.length - failed, images, failed };
}
