import type { DocumentIndex } from '../indexer/document-index.js';

export async function listCategories(index: DocumentIndex): Promise<string> {
  try {
    const stats = index.getStats();
    const categories = stats.categories;

    let output = `# SAP BTP Documentation Categories\n\n`;
    output += `**Total Documents:** ${stats.totalDocuments}\n`;
    output += `**Total Size:** ${(stats.totalSize / 1024 / 1024).toFixed(2)} MB\n\n`;

    output += `## Available Categories\n\n`;

    for (const category of categories) {
      const docs = index.getDocumentsByCategory(category);
      output += `### ${category}\n`;
      output += `- **Documents:** ${docs.length}\n`;
      output += `- **Top Documents:**\n`;

      // Show top 5 documents in category
      const topDocs = docs.slice(0, 5);
      for (const doc of topDocs) {
        output += `  - ${doc.title} (\`${doc.relativePath}\`)\n`;
      }

      if (docs.length > 5) {
        output += `  - ... and ${docs.length - 5} more\n`;
      }

      output += `\n`;
    }

    output += `---\n\n`;
    output += `Use \`search_btp_docs\` to search within specific categories.\n`;

    return output;
  } catch (error) {
    return `Error listing categories: ${error}`;
  }
}
