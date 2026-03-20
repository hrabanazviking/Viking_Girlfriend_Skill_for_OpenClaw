# rag_system.py — README_AI.md

## Purpose
RAG System for Norse Saga Engine
================================

Retrieval-Augmented Generation using chart data.
Indexes all chart files and provides relevant context for AI responses.

Features:
- BM25 ranking for relevance scoring
- Automatic chunking of large content
- Source attribution for retrieved content
- Caching for fast startup
- Integration with prompt builder

## Technical Architecture
- **Classes**: 4 main classes
  - `Chunk`: A searchable chunk of content from chart data.
  - `SearchResult`: A search result with relevance score.
  - `BM25Index`: BM25 ranking algorithm for text retrieval.

BM25 is a bag-of-words retrieval function that ranks doc
- **Functions**: 3 module-level functions

## Key Components
### `Chunk`
A searchable chunk of content from chart data.
**Methods**: __hash__

### `SearchResult`
A search result with relevance score.

### `BM25Index`
BM25 ranking algorithm for text retrieval.

BM25 is a bag-of-words retrieval function that ranks documents
based on query terms appearing in each document.
**Methods**: __init__, _tokenize, add_document, build_index, search

### `ChartRAGSystem`
RAG system for Norse Saga Engine chart data.

Indexes all chart files and provides context retrieval for AI prompts.
**Methods**: __init__, _get_cache_key, _load_cache, _save_cache, _chunk_text

## Dependencies
```
import json
import yaml
import math
import re
import hashlib
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
```

---
**Last Updated**: February 18, 2026 | v8.0.0
