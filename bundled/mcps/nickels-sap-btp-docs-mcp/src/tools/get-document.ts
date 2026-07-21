import type { DocumentIndex } from '../indexer/document-index.js';

export interface GetDocumentArgs {
  path: string;
}

export async function getDocument(
  index: DocumentIndex,
  args: GetDocumentArgs
): Promise<string> {
  const { path } = args;

  try {
    const doc = index.getDocumentByPath(path);

    if (!doc) {
      return `Document not found: ${path}\n\nTry searching for the document first using search_btp_docs.`;
    }

    let output = `# ${doc.metadata.title}\n\n`;
    output += `**Category:** ${doc.metadata.category}\n`;
    output += `**Path:** ${doc.metadata.relativePath}\n`;
    output += `**Last Modified:** ${doc.metadata.lastModified.toISOString()}\n\n`;

    if (doc.metadata.keywords && doc.metadata.keywords.length > 0) {
      output += `**Keywords:** ${doc.metadata.keywords.join(', ')}\n\n`;
    }

    output += `---\n\n`;

    // Add table of contents if document has sections
    if (doc.sections.length > 0) {
      output += `## Table of Contents\n\n`;
      for (const section of doc.sections) {
        const indent = '  '.repeat(section.level - 1);
        output += `${indent}- ${section.heading}\n`;
      }
      output += `\n---\n\n`;
    }

    // Add full content
    output += `## Content\n\n`;
    output += doc.fullContent;

    return output;
  } catch (error) {
    return `Error retrieving document: ${error}`;
  }
}
