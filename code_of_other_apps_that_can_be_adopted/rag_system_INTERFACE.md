# rag_system.py — INTERFACE.md

## Class: `Chunk`

A searchable chunk of content from chart data.

## Class: `SearchResult`

A search result with relevance score.

## Class: `BM25Index`

BM25 ranking algorithm for text retrieval.

BM25 is a bag-of-words retrieval function that ranks documents
based on query terms appearing in each document.

### `add_document(chunk)`
Add a document to the index.

### `build_index()`
Finalize the index after adding all documents.

### `search(query, top_k)`
Search for documents matching the query.

Args:
    query: Search query string
    top_k: Number of results to return
    
Returns:
    List of SearchResult objects sorted by relevance

## Class: `ChartRAGSystem`

RAG system for Norse Saga Engine chart data.

Indexes all chart files and provides context retrieval for AI prompts.

### `build_index(force_rebuild)`
Build the RAG index from all chart files.

Args:
    force_rebuild: Force rebuild even if cache exists

### `search(query, top_k, min_score)`
Search for relevant content.

Args:
    query: Search query
    top_k: Maximum results to return
    min_score: Minimum relevance score threshold
    
Returns:
    List of SearchResult objects

### `get_context_for_query(query, max_tokens)`
Get formatted context string for a query.

Args:
    query: The query to find context for
    max_tokens: Approximate maximum tokens for context
    
Returns:
    Formatted context string for inclusion in prompts

### `get_context_for_topics(topics, max_tokens)`
Get context for multiple topics.

Args:
    topics: List of topic strings to search for
    max_tokens: Approximate maximum tokens
    
Returns:
    Formatted context string

### `get_stats()`
Get statistics about the RAG index.

## Module Functions

### `get_rag_system(charts_path)`
Get or create the RAG system instance.

### `search_charts(query, top_k)`
Convenience function to search charts.

### `get_chart_context(query, max_tokens)`
Convenience function to get context for a query.

---
**Contract Version**: 1.0 | v8.0.0
