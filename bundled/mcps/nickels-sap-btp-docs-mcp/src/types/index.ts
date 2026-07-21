export interface DocumentMetadata {
  title: string;
  path: string;
  relativePath: string;
  category: string;
  lastModified: Date;
  size: number;
  headings: string[];
  keywords?: string[];
}

export interface DocumentContent {
  metadata: DocumentMetadata;
  content: string;
  sections: Section[];
}

export interface Section {
  heading: string;
  level: number;
  content: string;
  startLine: number;
  endLine: number;
}

export interface SearchResult {
  score: number;
  document: DocumentMetadata;
  matchedContent?: string;
  matchedSection?: Section;
}

export interface IndexedDocument {
  metadata: DocumentMetadata;
  fullContent: string;
  sections: Section[];
}

export interface ServiceArea {
  name: string;
  path: string;
  description: string;
}

export const SERVICE_AREAS: ServiceArea[] = [
  {
    name: 'development',
    path: 'docs/30-development',
    description: 'Development guides and tutorials for SAP BTP'
  },
  {
    name: 'administration',
    path: 'docs/50-administration-and-ops',
    description: 'Administration and operations documentation'
  },
  {
    name: 'integration',
    path: 'docs/40-extensions-and-integration',
    description: 'Integration patterns and extension guides'
  },
  {
    name: 'security',
    path: 'docs/60-security',
    description: 'Security and compliance documentation'
  }
];
