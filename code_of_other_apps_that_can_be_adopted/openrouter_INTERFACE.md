# openrouter.py — INTERFACE.md

## Class: `Message`

Chat message structure.

## Class: `CompletionResponse`

Response from completion API.

## Class: `OpenRouterError`

Base exception for OpenRouter errors.

## Class: `OpenRouterClient`

Async client for OpenRouter API.

Usage:
    client = OpenRouterClient(api_key="your-key")
    response = await client.complete([
        Message(role="system", content="You are a Norse saga narrator."),
        Message(role="user", content="Describe Uppsala at dusk.")
    ])
    print(response.content)

## Class: `SyncOpenRouterClient`

Synchronous wrapper around OpenRouterClient.

### `model()`
Expose model from async client.

### `provider()`
Expose provider from async client.

### `complete()`

### `narrate()`

### `character_speak()`

### `close()`

## Module Functions

### `list_models()`
Print available recommended models.

---
**Contract Version**: 1.0 | v8.0.0
