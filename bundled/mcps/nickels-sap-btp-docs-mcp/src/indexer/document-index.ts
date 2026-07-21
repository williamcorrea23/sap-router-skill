import { glob } from 'glob';
import Fuse from 'fuse.js';
import { MarkdownParser } from './markdown-parser.js';
import type { IndexedDocument, SearchResult, DocumentMetadata } from '../types/index.js';
import path from 'path';

export class DocumentIndex {
  private documents: IndexedDocument[] = [];
  private fuse: Fuse<IndexedDocument> | null = null;
  private parser: MarkdownParser;
  private docsRoot: string;

  constructor(docsRoot: string) {
    this.docsRoot = docsRoot;
    this.parser = new MarkdownParser();
  }

  async buildIndex(): Promise<void> {
    console.error('Building document index...');

    // Find all markdown files
    const pattern = path.join(this.docsRoot, '**/*.md');
    const files = await glob(pattern, {
      ignore: ['**/node_modules/**', '**/build/**']
    });

    console.error(`Found ${files.length} markdown files`);

    // Parse all documents
    for (const file of files) {
      try {
        const doc = await this.parser.parseDocument(file, this.docsRoot);
        this.documents.push({
          metadata: doc.metadata,
          fullContent: doc.content,
          sections: doc.sections
        });
      } catch (error) {
        console.error(`Error parsing ${file}:`, error);
      }
    }

    console.error(`Indexed ${this.documents.length} documents`);

    // Create Fuse search index
    this.fuse = new Fuse(this.documents, {
      keys: [
        { name: 'metadata.title', weight: 3 },
        { name: 'metadata.headings', weight: 2 },
        { name: 'fullContent', weight: 1 },
        { name: 'metadata.keywords', weight: 2.5 }
      ],
      includeScore: true,
      threshold: 0.4,
      ignoreLocation: true,
      minMatchCharLength: 3
    });

    console.error('Index built successfully');
  }

  search(query: string, category?: string, limit: number = 10): SearchResult[] {
    if (!this.fuse) {
      throw new Error('Index not built. Call buildIndex() first.');
    }

    let results = this.fuse.search(query, { limit: limit * 2 });

    // Filter by category if specified
    if (category && category !== 'all') {
      results = results.filter(r =>
        r.item.metadata.category.toLowerCase() === category.toLowerCase()
      );
    }

    // Take top results
    results = results.slice(0, limit);

    return results.map(result => ({
      score: 1 - (result.score || 0),
      document: result.item.metadata,
      matchedContent: this.extractMatchedContent(result.item, query)
    }));
  }

  private extractMatchedContent(doc: IndexedDocument, query: string, contextLength: number = 200): string {
    const queryLower = query.toLowerCase();
    const content = doc.fullContent.toLowerCase();

    const index = content.indexOf(queryLower);
    if (index === -1) {
      // Return first section or beginning of content
      return doc.fullContent.substring(0, contextLength) + '...';
    }

    const start = Math.max(0, index - contextLength / 2);
    const end = Math.min(doc.fullContent.length, index + queryLower.length + contextLength / 2);

    let excerpt = doc.fullContent.substring(start, end);
    if (start > 0) excerpt = '...' + excerpt;
    if (end < doc.fullContent.length) excerpt = excerpt + '...';

    return excerpt;
  }

  getDocumentByPath(relativePath: string): IndexedDocument | undefined {
    return this.documents.find(doc =>
      doc.metadata.relativePath === relativePath ||
      doc.metadata.path.endsWith(relativePath)
    );
  }

  getAllDocuments(): DocumentMetadata[] {
    return this.documents.map(doc => doc.metadata);
  }

  getDocumentsByCategory(category: string): DocumentMetadata[] {
    return this.documents
      .filter(doc => doc.metadata.category.toLowerCase() === category.toLowerCase())
      .map(doc => doc.metadata);
  }

  getCategories(): string[] {
    const categories = new Set(this.documents.map(doc => doc.metadata.category));
    return Array.from(categories).sort();
  }

  getStats(): { totalDocuments: number; categories: string[]; totalSize: number } {
    return {
      totalDocuments: this.documents.length,
      categories: this.getCategories(),
      totalSize: this.documents.reduce((sum, doc) => sum + doc.metadata.size, 0)
    };
  }
}
