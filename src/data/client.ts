import type { z } from 'zod';
import { indexSchema, storySchema, tagsSchema } from './schema';
import { typeset } from '../domain/typeset';
import type { Block, Index, Story, Tags } from './types';

const typesetBlock = (b: Block): Block =>
  b.type === 'image' ? { ...b, alt: typeset(b.alt) } : { ...b, text: typeset(b.text) };

const typesetIndex = (index: Index): Index => ({
  ...index,
  stories: index.stories.map((s) => ({ ...s, title: typeset(s.title) })),
});

const typesetStory = (story: Story): Story => ({
  ...story,
  title: typeset(story.title),
  moral: story.moral && typeset(story.moral),
  origin: story.origin && typeset(story.origin),
  blocks: story.blocks.map(typesetBlock),
});

export type DataErrorKind = 'network' | 'http' | 'invalid';

export class DataError extends Error {
  override name = 'DataError';
  constructor(
    readonly kind: DataErrorKind,
    message: string,
    readonly status?: number,
  ) {
    super(message);
  }
}

export const compendiumUrl = (path: string) => `${import.meta.env.BASE_URL}compendium/${path}`;

async function fetchJson<T>(path: string, schema: z.ZodType<T>): Promise<T> {
  let res: Response;
  try {
    res = await fetch(compendiumUrl(path));
  } catch (e) {
    throw new DataError('network', `Could not reach ${path}: ${String(e)}`);
  }
  if (!res.ok) throw new DataError('http', `${path} returned ${res.status}`, res.status);
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    throw new DataError('invalid', `${path} is not valid JSON`);
  }
  const parsed = schema.safeParse(body);
  if (!parsed.success) throw new DataError('invalid', `${path}: ${parsed.error.message}`);
  return parsed.data;
}

let indexPromise: Promise<Index> | null = null;
let tagsPromise: Promise<Tags> | null = null;
const storyPromises = new Map<string, Promise<Story>>();

export function loadIndex(): Promise<Index> {
  indexPromise ??= fetchJson('index.json', indexSchema).then(typesetIndex, (e: unknown) => {
    indexPromise = null;
    throw e;
  });
  return indexPromise;
}

export function loadTags(): Promise<Tags> {
  tagsPromise ??= fetchJson('tags.json', tagsSchema).catch((e: unknown) => {
    tagsPromise = null;
    throw e;
  });
  return tagsPromise;
}

export function loadStory(id: string): Promise<Story> {
  if (!/^[a-z0-9-]+$/.test(id)) return Promise.reject(new DataError('invalid', `Bad id ${id}`));
  let p = storyPromises.get(id);
  if (!p) {
    p = fetchJson(`stories/${id}.json`, storySchema).then(typesetStory, (e: unknown) => {
      storyPromises.delete(id);
      throw e;
    });
    storyPromises.set(id, p);
  }
  return p;
}

export function resetDataCache() {
  indexPromise = null;
  tagsPromise = null;
  storyPromises.clear();
}
