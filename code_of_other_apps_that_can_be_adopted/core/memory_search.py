from __future__ import annotations

from typing import Any, Callable, Iterable

try:
    from rank_bm25 import BM25Okapi
except Exception:  # pragma: no cover
    BM25Okapi = None


def rank_records(
    query: str,
    records: list[Any],
    *,
    curated_importance: dict[str, float],
    curated_mentions: dict[str, int],
    limit: int,
    semantic_enabled: bool,
    session_id: str,
    tokens: Callable[[str], list[str]],
    extract_entities: Callable[[str], dict[str, list[str]]],
    reasoning_intent_boosts: Callable[[str], dict[str, float]],
    query_has_temporal_intent: Callable[[str], bool],
    generate_embedding: Callable[[str], list[float] | None],
    query_similar_embeddings: Callable[[list[float], list[Any]], list[dict[str, Any]]],
    read_embeddings_map: Callable[[], dict[str, list[float]]],
    cosine_similarity: Callable[[list[float], list[float]], float],
    entity_match_score: Callable[[dict[str, list[str]], dict[str, list[str]]], float],
    recency_score: Callable[[str], float],
    record_temporal_anchor: Callable[[Any], str],
    memory_has_temporal_markers: Callable[[str], bool],
    bounded_confidence_score: Callable[[Any], float],
    normalize_reasoning_layer: Callable[[Any], str],
    decay_penalty: Callable[[Any], float],
    upcoming_event_boost: Callable[[Any], float],
    salience_boost: Callable[[dict[str, Any] | None], float],
    episodic_session_boost: Callable[[Any], float],
    semantic_bm25_weight: float,
    semantic_vector_weight: float,
    ranking_confidence_boost_max: float,
    temporal_intent_match_boost: float,
    temporal_intent_miss_penalty: float,
    bm25_class: Any = None,
) -> list[Any]:
    if not records:
        return []

    query_tokens = tokens(query)
    query_entities = extract_entities(query)
    reasoning_boosts = reasoning_intent_boosts(query)
    has_temporal_intent = query_has_temporal_intent(query)
    if not query_tokens:
        return records[-limit:][::-1]

    corpus_tokens = [tokens(str(getattr(item, "text", "") or "")) for item in records]
    corpus_entities = [extract_entities(str(getattr(item, "text", "") or "")) for item in records]
    query_token_set = set(query_tokens)

    resolved_bm25 = BM25Okapi if bm25_class is None else bm25_class
    if resolved_bm25 is None:
        bm25_scores = [0.0 for _ in records]
    else:
        bm25 = resolved_bm25(corpus_tokens)
        scores = bm25.get_scores(query_tokens)
        bm25_scores = [float(scores[idx]) for idx in range(len(records))]

    semantic_scores = [0.0 for _ in records]
    semantic_active = False
    if semantic_enabled:
        query_embedding = generate_embedding(query)
        if query_embedding is not None:
            try:
                similarity_hits = query_similar_embeddings(query_embedding, records)
            except Exception:
                similarity_hits = []
            if similarity_hits:
                score_by_id: dict[str, float] = {}
                for hit in similarity_hits:
                    if not isinstance(hit, dict):
                        continue
                    row_id = str(hit.get("record_id", "")).strip()
                    if not row_id:
                        continue
                    try:
                        score_by_id[row_id] = float(hit.get("score", 0.0) or 0.0)
                    except Exception:
                        continue
                if score_by_id:
                    for idx, row in enumerate(records):
                        semantic_scores[idx] = score_by_id.get(str(getattr(row, "id", "") or ""), 0.0)
                    semantic_active = True
            if not semantic_active:
                embeddings = read_embeddings_map()
                if embeddings:
                    for idx, row in enumerate(records):
                        vector = embeddings.get(str(getattr(row, "id", "") or ""))
                        if vector is None:
                            continue
                        semantic_scores[idx] = cosine_similarity(query_embedding, vector)
                    semantic_active = True

    scored: list[tuple[float, float, float, int]] = []
    for idx, row_tokens in enumerate(corpus_tokens):
        row = records[idx]
        overlap = len(query_token_set.intersection(row_tokens))
        entity_score = entity_match_score(query_entities, corpus_entities[idx])
        curated_boost = 0.0
        if str(getattr(row, "source", "") or "").startswith("curated:"):
            row_id = str(getattr(row, "id", "") or "")
            importance = curated_importance.get(row_id, 1.0)
            mentions = curated_mentions.get(row_id, 1)
            curated_boost = 0.75 + min(2.0, importance * 0.25) + min(1.0, mentions * 0.1)

        temporal_score = recency_score(record_temporal_anchor(row))
        row_text = str(getattr(row, "text", "") or "")
        if has_temporal_intent:
            if getattr(row, "happened_at", "") or memory_has_temporal_markers(row_text):
                temporal_score += temporal_intent_match_boost
            else:
                temporal_score -= temporal_intent_miss_penalty

        confidence_boost = bounded_confidence_score(getattr(row, "confidence", 1.0)) * ranking_confidence_boost_max
        reasoning_layer = normalize_reasoning_layer(getattr(row, "reasoning_layer", "fact"))
        reasoning_boost = reasoning_boosts.get(reasoning_layer, 0.0)
        row_decay_penalty = decay_penalty(row)
        row_upcoming_boost = upcoming_event_boost(row)
        relevance_signal = bool(
            overlap > 0
            or bm25_scores[idx] > 0.0
            or entity_score > 0.0
            or (semantic_active and semantic_scores[idx] > 0.05)
        )
        row_salience_boost = salience_boost(getattr(row, "metadata", {})) if relevance_signal else 0.0
        raw_episodic_boost = episodic_session_boost(row)
        episodic_boost = raw_episodic_boost if relevance_signal or has_temporal_intent else 0.0
        if not relevance_signal and episodic_boost > 0.0 and has_temporal_intent:
            relevance_signal = True

        ranking_score = bm25_scores[idx]
        ranking_score += (
            confidence_boost
            + reasoning_boost
            + entity_score
            + row_salience_boost
            + episodic_boost
            + row_upcoming_boost
            - row_decay_penalty
        )
        tie_breaker = (
            temporal_score
            + (confidence_boost * 0.5)
            + reasoning_boost
            + entity_score
            + row_salience_boost
            + episodic_boost
            + row_upcoming_boost
            - row_decay_penalty
        )
        if semantic_active:
            ranking_score = (
                semantic_bm25_weight * bm25_scores[idx]
                + semantic_vector_weight * semantic_scores[idx]
                + confidence_boost
                + reasoning_boost
                + entity_score
                + row_salience_boost
                + episodic_boost
                + row_upcoming_boost
                - row_decay_penalty
            )
            tie_breaker = (
                curated_boost
                + temporal_score
                + (confidence_boost * 0.5)
                + reasoning_boost
                + entity_score
                + row_salience_boost
                + episodic_boost
                + row_upcoming_boost
                - row_decay_penalty
            )
            scored.append((float(overlap) + entity_score + episodic_boost, ranking_score, tie_breaker, idx))
        else:
            scored.append((float(overlap) + curated_boost + entity_score + episodic_boost, ranking_score, tie_breaker, idx))

    scored.sort(key=lambda item: (item[0], item[1], item[2], item[3]), reverse=True)
    picked: list[Any] = []
    for overlap_score, relevance_score, _tie_breaker, idx in scored:
        if len(picked) >= limit:
            break
        if overlap_score <= 0 and relevance_score <= 0.0:
            continue
        picked.append(records[idx])
    return picked if picked else records[-limit:][::-1]


def search_records(
    query: str,
    *,
    limit: int,
    user_id: str,
    session_id: str,
    include_shared: bool,
    reasoning_layers: Iterable[str] | None,
    min_confidence: float | None,
    filters: dict[str, Any] | None,
    normalize_user_id: Callable[[str], str],
    collect_retrieval_records: Callable[..., tuple[list[Any], dict[str, float], dict[str, int], list[dict[str, Any]], bool]],
    rank_records_fn: Callable[..., list[Any]],
) -> list[Any]:
    bounded_limit = max(1, int(limit or 1))
    clean_user = normalize_user_id(user_id or "default")
    records, curated_importance, curated_mentions, _scopes, semantic_enabled = collect_retrieval_records(
        user_id=clean_user,
        include_shared=include_shared,
        session_id=session_id,
        reasoning_layers=reasoning_layers,
        min_confidence=min_confidence,
        filters=filters,
    )
    return rank_records_fn(
        query,
        records,
        curated_importance=curated_importance,
        curated_mentions=curated_mentions,
        limit=bounded_limit,
        semantic_enabled=semantic_enabled,
        session_id=session_id,
    )


__all__ = [
    "rank_records",
    "search_records",
]
