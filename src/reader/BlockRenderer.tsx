import type { Block } from '../data/types';
import { compendiumUrl } from '../data/client';
import { MarkedText, type Mark } from '../notes/MarkedText';
import imageSizes from '../data/imageSizes.json';

const sizes: Record<string, number[] | undefined> = imageSizes;

/** `priority`: the image is likely the first paint, so skip lazy loading. */
type Props = {
  block: Block;
  index: number;
  priority?: boolean;
  marks?: Mark[];
  onMark?: (id: string) => void;
};

export function BlockRenderer({ block, index, priority, marks, onMark }: Props) {
  const t = (text: string) => <MarkedText text={text} marks={marks} onMark={onMark} />;
  const data = { 'data-block': index };
  switch (block.type) {
    case 'p':
      return <p {...data}>{t(block.text)}</p>;
    case 'verse':
      return (
        <p className="verse" {...data}>
          {t(block.text)}
        </p>
      );
    case 'moral':
      return (
        <aside className="moral" aria-label="Moral" {...data}>
          <p>{t(block.text)}</p>
        </aside>
      );
    case 'heading':
      return (
        <h2 className="story-heading" {...data}>
          {t(block.text)}
        </h2>
      );
    case 'note':
      return (
        <aside className="note" aria-label="Note" {...data}>
          <small>{t(block.text)}</small>
        </aside>
      );
    case 'image': {
      const [width, height] = sizes[block.src] ?? [];
      return (
        <figure {...data}>
          <img
            src={compendiumUrl(block.src)}
            alt={block.alt}
            width={width}
            height={height}
            loading={priority ? 'eager' : 'lazy'}
            decoding="async"
            // React 18 only passes the lowercase attribute through.
            {...(priority && { fetchpriority: 'high' })}
          />
        </figure>
      );
    }
  }
}
