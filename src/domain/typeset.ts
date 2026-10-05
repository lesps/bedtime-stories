// Elisions where a leading apostrophe stands for missing letters, not an opening quote.
const ELISIONS = /'(?=(?:tis|twas|twere|twill|em|neath|n)\b)/gi;

/** Curly quotes and em dashes for source texts that use ASCII (`"`, `'`, `--`). */
export function typeset(text: string): string {
  if (!/["'-]/.test(text)) return text;
  return (
    text
      .replace(/--/g, '—')
      .replace(ELISIONS, '’')
      // A quote followed by space, end or punctuation closes; one opening a word after space,
      // start, a bracket or a dash opens; anything else closes.
      .replace(/"(?=$|[\s.,;:!?)\]}])/g, '”')
      .replace(/(^|[\s([{“‘—–-])"(?=\S)/g, '$1“')
      .replace(/"/g, '”')
      .replace(/(^|[\s([{“—–-])'(?=\S)/g, '$1‘')
      .replace(/'/g, '’')
  );
}
