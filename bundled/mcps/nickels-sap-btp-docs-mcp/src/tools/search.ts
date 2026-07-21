import type { DocumentIndex } from '../indexer/document-index.js';

export interface SearchDocsArgs {
  query: string;
  service_area?: string;
  limit?: number;
}

export async function searchDocs(
  index: DocumentIndex,
  args: SearchDocsArgs
): Promise<string> {
  const { query, service_area = 'all', limit = 10 } = args;

  try {
    const results = index.search(query, service_area, limit);

    if (results.length === 0) {
      return `No results found for query: "${query}"`;
    }

    let output = `# Search Results for "${query}"\n\n`;
    output += `Found ${results.length} relevant documents:\n\n`;

    for (let i = 0; i < results.length; i++) {
      const result = results[i];
      const doc = result.document;

      output += `## ${i + 1}. ${doc.title}\n\n`;
      output += `**Category:** ${doc.category}\n`;
      output += `**Path:** ${doc.relativePath}\n`;
      output += `**Relevance Score:** ${(result.score * 100).toFixed(1)}%\n\n`;

      if (result.matchedContent) {
        output += `**Excerpt:**\n\`\`\`\n${result.matchedContent}\n\`\`\`\n\n`;
      }

      output += `---\n\n`;
    }

    return output;
  } catch (error) {
    return `Error searching documents: ${error}`;
  }
}
