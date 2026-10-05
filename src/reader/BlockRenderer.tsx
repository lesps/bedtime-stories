import type { Block } from '../data/types';
import { compendiumUrl } from '../data/client';
import imageSizes from '../data/imageSizes.json';

const sizes: Record<string, number[] | undefined> = imageSizes;

/** `priority`: the image is likely the first paint, so skip lazy loading. */
type Props = { block: Block; index: number; priority?: boolean };

export function BlockRenderer({ block, index, priority }: Props) {
  const data = { 'data-block': index };
  switch (block.type) {
    case 'p':
      return <p {...data}>{block.text}</p>;
    case 'verse':
      return (
        <p className="verse" {...data}>
          {block.text}
        </p>
      );
    case 'moral':
      return (
        <aside className="moral" aria-label="Moral" {...data}>
          <p>{block.text}</p>
        </aside>
      );
    case 'heading':
      return (
        <h2 className="story-heading" {...data}>
          {block.text}
        </h2>
      );
    case 'note':
      return (
        <aside className="note" aria-label="Note" {...data}>
          <small>{block.text}</small>
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
