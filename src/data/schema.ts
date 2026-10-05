import { z } from 'zod';
import type { Block, Index, Story } from './types';

const flag = z.enum(['mature-themes', 'racial-slur']);

export const collectionSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  author: z.string().min(1),
  contributor: z.string().nullable(),
  firstPublished: z.number().int().nullable(),
  source: z.string().url(),
  license: z.literal('Public domain in the USA'),
  storyCount: z.number().int().nonnegative(),
});

const entryFields = {
  id: z.string().regex(/^[a-z0-9-]+--[a-z0-9-]+$/),
  collectionId: z.string().min(1),
  order: z.number().int().positive(),
  title: z.string().min(1),
  wordCount: z.number().int().nonnegative(),
  readingMinutes: z.number().int().min(1),
  excluded: z.boolean(),
  flags: z.array(flag),
};

export const indexEntrySchema = z.object({ ...entryFields, hasImages: z.boolean() });

export const indexSchema: z.ZodType<Index> = z.object({
  schemaVersion: z.literal(1),
  collections: z.array(collectionSchema),
  stories: z.array(indexEntrySchema),
});

const text = z.string();
export const blockSchema: z.ZodType<Block> = z.discriminatedUnion('type', [
  z.object({ type: z.literal('p'), text }),
  z.object({ type: z.literal('verse'), text }),
  z.object({ type: z.literal('moral'), text }),
  z.object({ type: z.literal('heading'), text }),
  z.object({ type: z.literal('note'), text }),
  z.object({ type: z.literal('image'), src: z.string().min(1), alt: z.string() }),
]);

export const storySchema: z.ZodType<Story> = z.object({
  ...entryFields,
  origin: z.string().nullable(),
  moral: z.string().nullable(),
  blocks: z.array(blockSchema).min(1),
});
