import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkFrontmatter from 'remark-frontmatter';
import { visit } from 'unist-util-visit';
import matter from 'gray-matter';
import type { DocumentContent, Section, DocumentMetadata } from '../types/index.js';
import { readFile } from 'fs/promises';
import { stat } from 'fs/promises';
import path from 'path';

export class MarkdownParser {
  async parseDocument(filePath: string, docsRoot: string): Promise<DocumentContent> {
    const content = await readFile(filePath, 'utf-8');
    const stats = await stat(filePath);

    // Parse frontmatter
    const { data: frontmatter, content: markdownContent } = matter(content);

    // Parse markdown AST
    const processor = unified()
      .use(remarkParse)
      .use(remarkGfm)
      .use(remarkFrontmatter);

    const tree = processor.parse(markdownContent);

    // Extract headings and sections
    const headings: string[] = [];
    const sections: Section[] = [];
    let currentSection: Section | undefined;
    let currentContent: string[] = [];
    let lineNumber = 0;

    visit(tree, (node: any) => {
      if (node.type === 'heading') {
        // Save previous section if exists
        if (currentSection) {
          currentSection.content = currentContent.join('\n').trim();
          currentSection.endLine = lineNumber - 1;
          sections.push(currentSection);
          currentContent = [];
        }

        // Extract heading text
        const headingText = this.extractText(node);
        headings.push(headingText);

        // Start new section
        currentSection = {
          heading: headingText,
          level: node.depth,
          content: '',
          startLine: lineNumber,
          endLine: lineNumber
        };
      } else if (node.type === 'text' || node.type === 'paragraph' || node.type === 'code') {
        if (currentSection) {
          currentContent.push(this.extractText(node));
        }
      }

      lineNumber++;
    });

    // Save last section
    if (currentSection) {
      currentSection.content = currentContent.join('\n').trim();
      currentSection.endLine = lineNumber;
      sections.push(currentSection);
    }

    // Determine category from path
    const relativePath = path.relative(docsRoot, filePath);
    const category = this.extractCategory(relativePath);

    const metadata: DocumentMetadata = {
      title: frontmatter.title || headings[0] || path.basename(filePath, '.md'),
      path: filePath,
      relativePath,
      category,
      lastModified: stats.mtime,
      size: stats.size,
      headings,
      keywords: frontmatter.keywords || []
    };

    return {
      metadata,
      content: markdownContent,
      sections
    };
  }

  private extractText(node: any): string {
    if (node.type === 'text') {
      return node.value;
    }

    if (node.type === 'code') {
      return node.value;
    }

    if (node.children) {
      return node.children.map((child: any) => this.extractText(child)).join('');
    }

    return '';
  }

  private extractCategory(relativePath: string): string {
    const parts = relativePath.split(path.sep);

    if (parts[0] === 'docs' && parts[1]) {
      // Extract category from folder name like "30-development"
      const folder = parts[1];
      const match = folder.match(/^\d+-(.+)$/);
      return match ? match[1] : folder;
    }

    return 'general';
  }
}
