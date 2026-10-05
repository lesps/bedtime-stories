import type { Block } from '../data/types';
import { compendiumUrl } from '../data/client';

type Props = { block: Block; index: number };

export function BlockRenderer({ block, index }: Props) {
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
    case 'image':
      return (
        <figure {...data}>
          <img src={compendiumUrl(block.src)} alt={block.alt} loading="lazy" decoding="async" />
        </figure>
      );
  }
}
