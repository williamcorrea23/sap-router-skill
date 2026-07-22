/**
 * Objects store the concatenation of all their files' sources, joined with
 * `* ===== <path> =====` header lines (see lib/parser/extract.ts). Evidence
 * line numbers (parser + validators) are file-local — this helper recovers
 * the per-file segments so evidence can be validated where it was cited.
 */
export interface SourceSegment {
  file: string;
  /** file-local source text */
  text: string;
}

const HEADER = /^\* ===== (.+) =====$/;

export function sourceSegments(storedSource: string, files: string[]): SourceSegment[] {
  const lines = storedSource.split("\n");
  const segments: SourceSegment[] = [];
  let current: { file: string; lines: string[] } | null = null;
  for (const line of lines) {
    const m = line.match(HEADER);
    if (m) {
      if (current) segments.push({ file: current.file, text: current.lines.join("\n") });
      current = { file: m[1], lines: [] };
      continue;
    }
    if (!current) {
      // single-file objects seeded without a header, or non-ABAP sources
      current = { file: files[0] ?? "", lines: [] };
    }
    current.lines.push(line);
  }
  if (current) segments.push({ file: current.file, text: current.lines.join("\n") });
  // drop the trailing blank line the join between files introduces
  return segments.map((s) => ({ ...s, text: s.text.replace(/\n$/, "") }));
}

/** Find the segment containing a verbatim quote; returns file + 1-based line. */
export function locateQuote(
  segments: SourceSegment[],
  quote: string
): { file: string; line: number; verbatim: string } | null {
  const needle = quote.trim();
  if (needle.length < 6) return null;
  for (const seg of segments) {
    const lines = seg.text.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(needle)) return { file: seg.file, line: i + 1, verbatim: lines[i].trim() };
    }
    // multi-line quotes: normalize whitespace and search the joined text
    const flatSeg = seg.text.replace(/\s+/g, " ");
    const flatNeedle = needle.replace(/\s+/g, " ");
    if (flatNeedle.length >= 12 && flatSeg.includes(flatNeedle)) {
      const firstLine = needle.split("\n")[0].trim();
      const lineIdx = lines.findIndex((l) => l.includes(firstLine));
      return { file: seg.file, line: lineIdx >= 0 ? lineIdx + 1 : 1, verbatim: flatNeedle.slice(0, 200) };
    }
  }
  return null;
}
