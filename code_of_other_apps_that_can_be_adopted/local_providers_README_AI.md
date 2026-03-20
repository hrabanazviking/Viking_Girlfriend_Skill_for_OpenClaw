# local_providers.py — README_AI.md

## Purpose
Local AI Provider Support (v4.5.0)
===================================
Provides local LLM backends as drop-in replacements for OpenRouter.

Supported providers:
- Ollama (default port 11434)
- LM Studio (OpenAI-compatible, default port 1234)
- Any OpenAI-compatible API (KoboldCpp, text-generation-webui, etc.)

Usage in config.yaml:
    ai_provider: "ollama"        # or "lmstudio", "openai_compat"
    local_ai:
        provider: "ollama"
        base_url: "http://localhost:11434"
        model: "

## Technical Architecture
- **Classes**: 3 main classes
  - `LocalAIError`: Exception raised by local AI providers.
  - `OllamaClient`: Client for Ollama (https://ollama.ai).

Ollama runs models locally and exposes them via REST API.
De
  - `LMStudioClient`: Client for LM Studio and any OpenAI-compatible API.

Works with:
- LM Studio (default: http://localh
- **Functions**: 1 module-level functions

## Key Components
### `LocalAIError`
Exception raised by local AI providers.

### `OllamaClient`
Client for Ollama (https://ollama.ai).

Ollama runs models locally and exposes them via REST API.
Default endpoint: http://localhost:11434
**Methods**: __init__, complete, list_models

### `LMStudioClient`
Client for LM Studio and any OpenAI-compatible API.

Works with:
- LM Studio (default: http://localhost:1234)
- KoboldCpp (http://localhost:5001)
- text-generation-webui with OpenAI extension
- Any ot
**Methods**: __init__, complete

## Dependencies
```
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from ai.openrouter import Message, CompletionResponse
```

---
**Last Updated**: February 18, 2026 | v8.0.0
