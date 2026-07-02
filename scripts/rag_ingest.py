#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Ingest and Search Engine v5.0.0 (Pure Python, Offline-first)

Ingests SAP Notes (YAML) and Module Maps (Markdown), index them using a lightweight
TF-IDF vectorizer built in pure Python, and offers CLI search.
"""

import os
import re
import sys
import json
import math
import argparse
import yaml
from pathlib import Path

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "references", "data")
MAPS_DIR = os.path.join(ROOT_DIR, "references", "module_maps")
INDEX_PATH = os.path.join(ROOT_DIR, ".rag_index.json")

# Stopwords list for lightweight tokenization
STOPWORDS = {
    "the", "and", "a", "of", "to", "in", "is", "that", "it", "on", "for", "with", 
    "as", "was", "at", "by", "an", "be", "this", "are", "or", "from", "at", "about",
    "an", "but", "by", "if", "not", "their", "then", "there", "these", "they", "this",
    "o", "a", "e", "os", "as", "de", "do", "da", "em", "para", "um", "uma", "com", "se",
    "한", "은", "는", "이", "가", "을", "를", "에", "의", "로", "과", "와"
}

def tokenize(text):
    """Normalize and tokenize text, removing punctuation and stopwords."""
    if not text:
        return []
    # Replace non-alphanumeric with spaces, keep Korean character blocks
    text = re.sub(r'[^a-zA-Z0-9\s\uac00-\ud7a3]', ' ', text.lower())
    words = text.split()
    return [w for w in words if w not in STOPWORDS and len(w) > 1]

class PureRAG:
    def __init__(self):
        self.documents = [] # List of {"id": str, "title": str, "content": str, "type": str, "source": str}
        self.vocab = {}      # Word -> Term ID
        self.idf = {}        # Word -> IDF score
        self.doc_vectors = [] # List of sparse document vectors: {term_id: tf-idf}

    def add_document(self, doc_id, title, content, doc_type, source):
        self.documents.append({
            "id": doc_id,
            "title": title,
            "content": content,
            "type": doc_type,
            "source": source
        })

    def build_index(self):
        """Calculate TF-IDF representations for all documents."""
        # 1. Tokenize and calculate TF for all documents
        doc_tfs = []
        doc_counts = {} # Word -> doc count
        
        for doc in self.documents:
            tokens = tokenize(doc["title"] + " " + doc["content"])
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            doc_tfs.append(tf)
            
            # Count document frequencies
            for word in tf.keys():
                doc_counts[word] = doc_counts.get(word, 0) + 1

        # 2. Build vocabulary and calculate IDF
        num_docs = len(self.documents)
        if num_docs == 0:
            return

        self.vocab = {word: idx for idx, word in enumerate(doc_counts.keys())}
        
        for word, count in doc_counts.items():
            # Add smoothing to avoid division by zero
            self.idf[word] = math.log(1.0 + (num_docs / (1.0 + count)))

        # 3. Build document TF-IDF vectors
        self.doc_vectors = []
        for i, tf in enumerate(doc_tfs):
            vector = {}
            doc_len_sq = 0.0
            
            for word, count in tf.items():
                term_id = self.vocab[word]
                tfidf = count * self.idf[word]
                vector[str(term_id)] = tfidf
                doc_len_sq += tfidf ** 2
                
            # Normalize vector
            doc_len = math.sqrt(doc_len_sq)
            if doc_len > 0:
                for term_id in vector:
                    vector[term_id] /= doc_len
                    
            self.doc_vectors.append({
                "vector": vector,
                "norm": doc_len
            })

    def search(self, query, top_n=5):
        """Search index using Cosine Similarity on TF-IDF vectors."""
        query_tokens = tokenize(query)
        if not query_tokens or not self.vocab:
            return []

        # 1. Compute query TF-IDF vector
        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        query_vector = {}
        query_len_sq = 0.0
        for word, count in query_tf.items():
            if word in self.vocab:
                term_id = self.vocab[word]
                tfidf = count * self.idf[word]
                query_vector[term_id] = tfidf
                query_len_sq += tfidf ** 2

        query_len = math.sqrt(query_len_sq)
        if query_len == 0:
            return []

        # Normalize query vector
        for term_id in query_vector:
            query_vector[term_id] /= query_len

        # 2. Compute similarity scores
        scores = []
        for i, doc_vec in enumerate(self.doc_vectors):
            score = 0.0
            vector = doc_vec["vector"]
            # Dot product
            for term_id, val in query_vector.items():
                str_term_id = str(term_id)
                if str_term_id in vector:
                    score += val * vector[str_term_id]
            
            if score > 0:
                scores.append((score, self.documents[i]))

        # Sort and return top_n
        scores.sort(key=lambda x: x[0], reverse=True)
        return [{"score": round(score, 4), "doc": doc} for score, doc in scores[:top_n]]

    def save_index(self, filepath):
        """Save index to JSON."""
        data = {
            "documents": self.documents,
            "vocab": self.vocab,
            "idf": self.idf,
            "doc_vectors": self.doc_vectors
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_index(self, filepath):
        """Load index from JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.documents = data["documents"]
        self.vocab = data["vocab"]
        self.idf = data["idf"]
        self.doc_vectors = data["doc_vectors"]


def run_ingestion():
    rag = PureRAG()

    # 1. Load SAP Notes (YAML)
    notes_path = os.path.join(DATA_DIR, "sap-notes.yaml")
    if os.path.exists(notes_path):
        try:
            with open(notes_path, "r", encoding="utf-8") as f:
                notes_data = yaml.safe_load(f)
            if notes_data and "notes" in notes_data:
                for note_info in notes_data["notes"]:
                    note_id = note_info.get("id", "UNKNOWN")
                    title = note_info.get("title", f"SAP Note {note_id}")
                    content = (
                        note_info.get("symptoms", "") + " " + 
                        note_info.get("solution", "") + " " + 
                        " ".join(note_info.get("keywords", []))
                    )
                    rag.add_document(
                        doc_id=str(note_id),
                        title=title,
                        content=content,
                        doc_type="sap_note",
                        source="sap-notes.yaml"
                    )
            print(f"Loaded SAP Notes from {notes_path}")
        except Exception as e:
            print(f"Warning: Failed to load SAP Notes: {e}")

    # 2. Load Module Maps (Markdown)
    if os.path.exists(MAPS_DIR):
        for filename in os.listdir(MAPS_DIR):
            if filename.endswith(".md"):
                file_path = os.path.join(MAPS_DIR, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    
                    # Split markdown into sections by headings
                    sections = re.split(r'\n(##+ .*)\n', md_content)
                    current_heading = "Overview"
                    
                    # Store first block
                    if sections:
                        rag.add_document(
                            doc_id=f"{filename}#overview",
                            title=f"{filename} — Overview",
                            content=sections[0],
                            doc_type="module_map",
                            source=filename
                        )
                        
                    # Store remaining blocks
                    for idx in range(1, len(sections), 2):
                        heading = sections[idx].strip("# ")
                        body = sections[idx+1] if idx+1 < len(sections) else ""
                        rag.add_document(
                            doc_id=f"{filename}#{heading.lower().replace(' ', '-')}",
                            title=f"{filename} — {heading}",
                            content=body,
                            doc_type="module_map",
                            source=filename
                        )
                except Exception as e:
                    print(f"Warning: Failed to parse {filename}: {e}")
        print(f"Loaded Module Maps from {MAPS_DIR}")

    rag.build_index()
    rag.save_index(INDEX_PATH)
    print(f"Ingested {len(rag.documents)} documents. Index saved to {INDEX_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Pure Python RAG Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest subparser
    subparsers.add_parser("ingest", help="Ingest documents and rebuild the index")

    # search subparser
    search_parser = subparsers.add_parser("search", help="Search the index")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--top", type=int, default=3, help="Number of top results to return")

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingestion()
    elif args.command == "search":
        rag = PureRAG()
        if not os.path.exists(INDEX_PATH):
            print(f"Index file {INDEX_PATH} not found. Running auto-ingestion...")
            run_ingestion()
        
        try:
            rag.load_index(INDEX_PATH)
        except Exception as e:
            print(f"Error: Failed to load index: {e}", file=sys.stderr)
            sys.exit(1)

        results = rag.search(args.query, top_n=args.top)
        print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
