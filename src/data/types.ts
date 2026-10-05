export type Flag = 'mature-themes' | 'racial-slur' | 'antisemitic-caricature';

export type Collection = {
  id: string;
  title: string;
  author: string;
  contributor: string | null;
  firstPublished: number | null;
  source: string;
  license: 'Public domain in the USA';
  storyCount: number;
  language: string;
  /** ISO 639-1 code of the source language, e.g. `de`, `ja`. */
  originalLanguage: string;
};

export type IndexEntry = {
  id: string;
  collectionId: string;
  order: number;
  title: string;
  wordCount: number;
  readingMinutes: number;
  excluded: boolean;
  flags: Flag[];
  hasImages: boolean;
  /** Shared by different translations of the same tale, e.g. `grimm-khm-015`. */
  workId?: string;
};

export type Index = {
  schemaVersion: 1;
  collections: Collection[];
  stories: IndexEntry[];
};

export type Block =
  | { type: 'p'; text: string }
  | { type: 'verse'; text: string }
  | { type: 'moral'; text: string }
  | { type: 'heading'; text: string }
  | { type: 'note'; text: string }
  | { type: 'image'; src: string; alt: string };

export type Story = Omit<IndexEntry, 'hasImages'> & {
  origin: string | null;
  moral: string | null;
  blocks: Block[];
  /** Per-story publication year and source, where a collection spans several books (Potter). */
  firstPublished?: number;
  source?: string;
  /** Title in the source language (Hunt). */
  originalTitle?: string;
};
