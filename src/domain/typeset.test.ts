import { describe, expect, it } from 'vitest';
import { typeset } from './typeset';

describe('typeset', () => {
  it.each([
    ['"Hello," said the Fox.', '“Hello,” said the Fox.'],
    ['He said, "Go!" and left.', 'He said, “Go!” and left.'],
    ["the girl's heart", 'the girl’s heart'],
    ["I'll tell thee what I'll do", 'I’ll tell thee what I’ll do'],
    ["'Come here,' said she.", '‘Come here,’ said she.'],
    ["the boys' caps", 'the boys’ caps'],
    ["'Twas the night; 'tis cold; give 'em bread", '’Twas the night; ’tis cold; give ’em bread'],
    ['wait--what?', 'wait—what?'],
    ['wait -- what?', 'wait — what?'],
    ['("Run")', '(“Run”)'],
    ['it turned out--" "Buzz! Buzz!"', 'it turned out—” “Buzz! Buzz!”'],
    ['"Why certainly——" began the Tortoise', '“Why certainly——” began the Tortoise'],
    ['"Stop!"', '“Stop!”'],
    ['he cried--"Run!"', 'he cried—“Run!”'],
    ['"\'Tis I," he said.', '“’Tis I,” he said.'],
    ['Already “curly” and ’tis fine — ok', 'Already “curly” and ’tis fine — ok'],
    ['  indented verse\n  keeps "spaces"', '  indented verse\n  keeps “spaces”'],
  ])('%j → %j', (input, expected) => expect(typeset(input)).toBe(expected));
});
