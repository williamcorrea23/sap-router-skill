import type { DocumentIndex } from '../indexer/document-index.js';

export interface GetServiceDocsArgs {
  service_name: string;
}

export async function getServiceDocs(
  index: DocumentIndex,
  args: GetServiceDocsArgs
): Promise<string> {
  const { service_name } = args;

  try {
    // Search for the service in documentation
    const results = index.search(service_name, undefined, 5);

    if (results.length === 0) {
      return `No documentation found for service: "${service_name}"\n\nTry searching with a different term or check the service name.`;
    }

    let output = `# SAP BTP Service: ${service_name}\n\n`;
    output += `Found ${results.length} relevant documentation pages:\n\n`;

    for (let i = 0; i < results.length; i++) {
      const result = results[i];
      const doc = result.document;

      output += `## ${i + 1}. ${doc.title}\n\n`;
      output += `**Category:** ${doc.category}\n`;
      output += `**Path:** ${doc.relativePath}\n`;
      output += `**Relevance:** ${(result.score * 100).toFixed(1)}%\n\n`;

      // Get full document content for the top result
      if (i === 0) {
        const fullDoc = index.getDocumentByPath(doc.relativePath);
        if (fullDoc) {
          output += `### Overview\n\n`;

          // Show first section or summary
          if (fullDoc.sections.length > 0) {
            const firstSection = fullDoc.sections[0];
            output += `${firstSection.content}\n\n`;
          }

          output += `### Quick Links\n\n`;
          output += `To view the complete documentation, use the \`get_btp_document\` tool with path: \`${doc.relativePath}\`\n\n`;
        }
      } else {
        if (result.matchedContent) {
          output += `**Excerpt:**\n\`\`\`\n${result.matchedContent}\n\`\`\`\n\n`;
        }
      }

      output += `---\n\n`;
    }

    return output;
  } catch (error) {
    return `Error retrieving service documentation: ${error}`;
  }
}
