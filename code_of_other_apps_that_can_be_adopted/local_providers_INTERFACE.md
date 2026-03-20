# local_providers.py — INTERFACE.md

## Class: `LocalAIError`

Exception raised by local AI providers.

## Class: `OllamaClient`

Client for Ollama (https://ollama.ai).

Ollama runs models locally and exposes them via REST API.
Default endpoint: http://localhost:11434

### `complete(messages)`
Send messages to Ollama's chat endpoint.

Compatible with the SyncOpenRouterClient interface.

### `list_models()`
List available Ollama models.

## Class: `LMStudioClient`

Client for LM Studio and any OpenAI-compatible API.

Works with:
- LM Studio (default: http://localhost:1234)
- KoboldCpp (http://localhost:5001)
- text-generation-webui with OpenAI extension
- Any other OpenAI-compatible local server

### `complete(messages)`
Send messages to an OpenAI-compatible chat completions endpoint.

Compatible with the SyncOpenRouterClient interface.

## Module Functions

### `create_local_client(config)`
Factory function to create the appropriate local AI client.

Args:
    config: Configuration dict with provider settings
    
Returns:
    Client instance (OllamaClient or LMStudioClient)

Config example:
    local_ai:
        provider: "ollama"       # or "lmstudio", "openai_compat"
        base_url: "http://localhost:11434"
        model: "llama3.1:8b"
        temperature: 0.8
        max_tokens: 4096

---
**Contract Version**: 1.0 | v8.0.0
