# OPENCLAW_PATCH_PROPOSAL.md
# Proposed Code Contributions to OpenClaw: Context Resilience & Security Hardening
**Authored by**: Runa Gridweaver
**Date**: 2026-03-21
**Status**: PLANNING DOCUMENT — not yet submitted. Consult with Volmarr before any submission.

> This is an MD design document. No actual patch has been written yet.
> Proposed code is TypeScript/JavaScript matching OpenClaw's conventions.
> See OPENCLAW_COMMS_CULTURE.md for how to approach the team.

---

## Executive Summary

We have identified three concrete, fixable security gaps in the OpenClaw Gateway that we believe align directly with the project's stated VISION.md priorities ("Security and safe defaults" is #1). We have already implemented analogous solutions in our own Sigrid skill. This document proposes how the same protections could be contributed upstream in TypeScript, matching OpenClaw's code style.

The three proposals are:
1. **Pluggable Embedding Provider** — replace the hard-wired Voyage AI dependency with a configurable interface so operators can use local providers (Ollama/Nomic)
2. **DirectiveGuard** — a context-window monitor that re-injects system directives before Compaction evicts them
3. **Gateway-level Input Sanitizer** — a thin prompt-injection scan layer that fires before user input reaches the model context

These are deliberately small and narrowly scoped. We will not propose these as a bundle — they would be separate PRs in sequence after Discord alignment.

---

## Proposal 1 — Pluggable Embedding Provider (Priority: HIGH)

### Problem

The OpenClaw Gateway currently has a hard dependency on Voyage AI for internal memory embeddings. Every conversation that triggers memory storage sends context text to the Voyage AI API. This violates the project's own core value proposition ("lives on your hard drive," local-first) and constitutes a privacy leak for operators who believe their data is not leaving their machine.

From our local security research:
> "Current versions of OpenClaw have a rigid dependency on Voyage AI (an external API) for internal memory embeddings. As an architect, you must recognize this as a privacy leak."

**Framing for the OpenClaw team:**
> "The Operator Trust Model in SECURITY.md is clear: the operator's data stays with the operator. The Voyage AI embedding call currently breaks this contract without the operator's explicit awareness."

### Proposed solution (TypeScript)

Add an `EmbeddingProvider` interface that the Gateway uses for all embedding calls, with two implementations: `VoyageAiEmbeddingProvider` (existing behavior) and `OllamaEmbeddingProvider` (new local option).

```typescript
// gateway/src/memory/embedding-provider.ts

/**
 * EmbeddingProvider — pluggable interface for text embeddings.
 *
 * The Gateway calls embed() for all memory storage and retrieval.
 * Implementations: VoyageAiEmbeddingProvider (default, cloud),
 * OllamaEmbeddingProvider (local, privacy-preserving).
 */
export interface EmbeddingProvider {
  /** Embed a single text chunk. Returns a float[] vector. */
  embed(text: string): Promise<number[]>;

  /** Batch-embed for ingest efficiency. Default impl: sequential embed(). */
  embedBatch(texts: string[]): Promise<number[][]>;

  /** Human-readable name for logging and diagnostics (openclaw doctor). */
  readonly providerName: string;
}

// --- Existing provider (no behavior change) ---

export class VoyageAiEmbeddingProvider implements EmbeddingProvider {
  readonly providerName = "voyage-ai";

  constructor(private readonly apiKey: string, private readonly model = "voyage-3") {}

  async embed(text: string): Promise<number[]> {
    // existing Voyage AI API call logic (moved here from inline usage)
    // ... unchanged implementation ...
    return [];
  }

  async embedBatch(texts: string[]): Promise<number[][]> {
    return Promise.all(texts.map((t) => this.embed(t)));
  }
}

// --- New local provider ---

/**
 * OllamaEmbeddingProvider — calls a local Ollama instance for embeddings.
 *
 * Default model: nomic-embed-text (768-dim, Apache 2.0, ~274MB).
 * Requires: Ollama running at ollamaBaseUrl with the model pulled.
 *
 * Privacy: zero external calls. All embedding computation is local.
 *
 * Usage in workspace/config.yaml:
 *   embedding:
 *     provider: ollama
 *     model: nomic-embed-text
 *     baseUrl: http://localhost:11434
 */
export class OllamaEmbeddingProvider implements EmbeddingProvider {
  readonly providerName = "ollama";

  constructor(
    private readonly baseUrl = "http://localhost:11434",
    private readonly model = "nomic-embed-text"
  ) {}

  async embed(text: string): Promise<number[]> {
    const response = await fetch(`${this.baseUrl}/api/embeddings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: this.model, prompt: text }),
    });
    if (!response.ok) {
      throw new Error(
        `Ollama embedding failed: ${response.status} ${response.statusText}`
      );
    }
    const data = (await response.json()) as { embedding: number[] };
    return data.embedding;
  }

  async embedBatch(texts: string[]): Promise<number[][]> {
    // Sequential for now; Ollama doesn't have a native batch endpoint
    return Promise.all(texts.map((t) => this.embed(t)));
  }
}
```

**Config schema addition** (`workspace/config.yaml` or wherever Gateway reads config):
```yaml
# NEW: embedding block (optional — defaults to voyage-ai for backward compatibility)
embedding:
  provider: ollama          # "voyage-ai" (default) | "ollama"
  model: nomic-embed-text   # for ollama; ignored for voyage-ai
  baseUrl: http://localhost:11434   # for ollama; ignored for voyage-ai
```

**Factory function** (called during gateway startup):
```typescript
// gateway/src/memory/embedding-factory.ts

export function createEmbeddingProvider(config: GatewayConfig): EmbeddingProvider {
  const embeddingCfg = config.embedding ?? {};
  const provider = embeddingCfg.provider ?? "voyage-ai";

  switch (provider) {
    case "ollama":
      return new OllamaEmbeddingProvider(
        embeddingCfg.baseUrl ?? "http://localhost:11434",
        embeddingCfg.model ?? "nomic-embed-text"
      );
    case "voyage-ai":
    default:
      const apiKey = process.env.VOYAGE_AI_API_KEY;
      if (!apiKey) {
        throw new Error(
          "[OpenClaw] VOYAGE_AI_API_KEY is not set. " +
          "Set it or switch to a local embedding provider: " +
          "https://docs.openclaw.ai/embedding-providers"
        );
      }
      return new VoyageAiEmbeddingProvider(apiKey);
  }
}
```

### What changes in the Gateway?
- Any place that currently calls `voyageAi.embed(...)` directly → replaced with `embeddingProvider.embed(...)`
- `createEmbeddingProvider(config)` called once at startup and stored on the app context
- No other behavior changes; no new dependencies in core (fetch is already available in Node 24)

### PR scope estimate
- ~200–300 lines total (new interface file, Ollama implementation, factory, 2–3 call-site substitutions)
- Well under the 5,000-line limit
- No breaking change: operators who don't set `embedding.provider` get the existing Voyage AI behavior

---

## Proposal 2 — DirectiveGuard (ContextGuard for the Gateway)

### Problem

When a session grows long enough to approach the 131,072-token limit, OpenClaw's Compaction system kicks in — but Compaction prunes from the bottom of the session history, not the top. The system prompt / operator directives sit at the top of the context stack and are the **first tokens evicted** when the raw context exceeds the model's attention window before Compaction has a chance to run. The result is that the operator's custom persona, instructions, and guardrails silently disappear mid-session.

The project calls this "Directive Eviction." We have been calling it "soul eviction" in our internal docs. Either way, it is a real failure mode for long sessions.

**Framing for the OpenClaw team:**
> "Compaction is designed to keep sessions alive, not to protect the operator directive block. When the Gateway doesn't fire Compaction soon enough, the directives — which sit at the top of the stack — are the first to leave the attention window. The session continues but the operator's intent is gone."

### Proposed solution (TypeScript)

Add a `DirectiveGuard` class that the Gateway checks before each completion call:

```typescript
// gateway/src/session/directive-guard.ts

/**
 * DirectiveGuard — monitors context token usage and re-anchors the
 * system directive block before it can be silently evicted.
 *
 * Fires when: estimated token count / max context tokens >= threshold.
 *
 * On overflow warning:
 *   1. Logs a WARNING visible in `openclaw doctor` output
 *   2. Prepends a compact version of the operator's system directives
 *      to the next completion message list (ahead of history)
 *   3. Emits a `directive.overflow_warning` event on the Gateway event bus
 *
 * Token counting: uses tiktoken if available, falls back to charCount / 4.
 */

import { encode } from "gpt-tokenizer"; // already in dep tree (used for other token ops)

export interface DirectiveGuardConfig {
  /** Max context tokens for the model. Default: 131072 (LLaMA-3 / GPT-4o class). */
  maxContextTokens?: number;
  /** Ratio at which to fire the overflow warning and re-inject. Default: 0.80 */
  overflowThresholdRatio?: number;
  /** Max chars to include in the re-injected directive anchor. Default: 1500 */
  directiveAnchorMaxChars?: number;
  /** If false, only warns — does not re-inject. Default: true */
  reinjectionEnabled?: boolean;
}

export interface DirectiveGuardResult {
  withinBudget: boolean;
  tokenCount: number;
  overflowRatio: number;
  /** If set, prepend this to the messages list before the completion call. */
  anchorInjection?: { role: "system"; content: string };
}

export class DirectiveGuard {
  private readonly maxContextTokens: number;
  private readonly threshold: number;
  private readonly anchorMaxChars: number;
  private readonly reinjectionEnabled: boolean;

  constructor(config: DirectiveGuardConfig = {}) {
    this.maxContextTokens = config.maxContextTokens ?? 131_072;
    this.threshold = config.overflowThresholdRatio ?? 0.8;
    this.anchorMaxChars = config.directiveAnchorMaxChars ?? 1500;
    this.reinjectionEnabled = config.reinjectionEnabled ?? true;
  }

  /**
   * Check the assembled messages list before sending to the model.
   *
   * @param messages  The full messages list (system + history + current user turn)
   * @param systemDirective  The operator's original system directive text
   * @returns DirectiveGuardResult — call anchorInjection?.[0] onto messages if set
   */
  check(
    messages: Array<{ role: string; content: string }>,
    systemDirective: string
  ): DirectiveGuardResult {
    const fullText = messages.map((m) => m.content).join(" ");
    const tokenCount = this.countTokens(fullText);
    const overflowRatio = tokenCount / this.maxContextTokens;
    const withinBudget = overflowRatio < this.threshold;

    if (withinBudget) {
      return { withinBudget: true, tokenCount, overflowRatio };
    }

    // Overflow: build anchor block
    const anchorContent = this.buildAnchor(systemDirective);
    const anchorInjection = this.reinjectionEnabled
      ? { role: "system" as const, content: anchorContent }
      : undefined;

    return {
      withinBudget: false,
      tokenCount,
      overflowRatio,
      anchorInjection,
    };
  }

  private buildAnchor(directive: string): string {
    const trimmed = directive.slice(0, this.anchorMaxChars);
    return `[DIRECTIVE ANCHOR — session near context limit; operator directives re-injected]\n\n${trimmed}`;
  }

  private countTokens(text: string): number {
    try {
      return encode(text).length;
    } catch {
      return Math.ceil(text.length / 4);
    }
  }
}
```

**Integration point** — inside the Gateway's completion pipeline, before the model call:
```typescript
// Pseudocode — where the Gateway calls the model for a session turn:

const guardResult = directiveGuard.check(messages, session.systemDirective);

if (!guardResult.withinBudget) {
  logger.warn(
    `[DirectiveGuard] Context at ${(guardResult.overflowRatio * 100).toFixed(1)}% ` +
    `(${guardResult.tokenCount} tokens). Re-injecting directives.`
  );
  gateway.eventBus.emit("directive.overflow_warning", {
    sessionId: session.id,
    tokenCount: guardResult.tokenCount,
    overflowRatio: guardResult.overflowRatio,
  });
}

if (guardResult.anchorInjection) {
  messages = [guardResult.anchorInjection, ...messages];
}

const response = await model.complete(messages);
```

### PR scope estimate
- ~150–200 lines (new file + ~15-line integration in the completion pipeline)
- No new dependencies (gpt-tokenizer is already in the dep tree)
- Config: new optional `directiveGuard` block in workspace config (safe defaults: disabled unless opted in)

---

## Proposal 3 — Gateway Input Sanitizer (Thin Injection Scan Layer)

### Problem

User input (from WhatsApp/Telegram/Discord/Slack) arrives in the Gateway's incoming message pipeline and is passed directly to the model context without sanitization. Prompt injection attacks ("Ignore all previous instructions and...") can override operator directives because the model sees them as continuation of its instruction set.

The Gateway's trust model (SECURITY.md) explicitly notes that prompt injection is an issue but delegates defense to skill authors. A thin framework-level scan would:
1. Catch the most obvious patterns before they reach the model
2. Give skill authors an opt-out rather than requiring them to build their own scanner
3. Align with Priority #1 (Security and safe defaults) without adding complexity for operators who don't need it

### Proposed solution (TypeScript)

```typescript
// gateway/src/security/input-sanitizer.ts

/**
 * InputSanitizer — thin prompt-injection detection layer.
 *
 * Scans incoming user messages before they enter the model context.
 * Block-severity patterns are rejected and a safe error response is returned.
 * Warn-severity patterns are logged but allowed through.
 *
 * Operators opt-in via workspace config:
 *   security:
 *     inputSanitizer:
 *       enabled: true
 *       blockSeverity: block   # "block" | "warn-only"
 */

export type SanitizeSeverity = "block" | "warn";

export interface SanitizePattern {
  name: string;
  severity: SanitizeSeverity;
  pattern: RegExp;
}

export interface SanitizeResult {
  safe: boolean;
  patternName?: string;
  severity?: SanitizeSeverity;
  matchedText?: string;
}

// Built-in patterns covering the most common injection forms
const BUILT_IN_PATTERNS: SanitizePattern[] = [
  {
    name: "ignore_previous",
    severity: "block",
    pattern: /\b(ignore|disregard|forget|override)\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|directives?|context|system|prompt)/gi,
  },
  {
    name: "you_are_now",
    severity: "block",
    pattern: /\byou\s+are\s+now\s+(a\s+|an\s+)?(different|new|another|uncensored|unfiltered|jailbroken|free|unrestricted)/gi,
  },
  {
    name: "system_override",
    severity: "block",
    pattern: /\b(system\s+override|jailbreak|dan\s+mode|developer\s+mode|god\s+mode|unrestricted\s+mode)/gi,
  },
  {
    name: "reveal_prompt",
    severity: "warn",
    pattern: /\b(repeat|print|show|output|reveal|tell\s+me)\s+.{0,30}(system\s+prompt|initial\s+instructions?|hidden\s+instructions?|full\s+prompt)/gi,
  },
  {
    name: "do_anything_now",
    severity: "warn",
    pattern: /\b(do\s+anything\s+now|you\s+can\s+do\s+anything|no\s+restrictions?|bypass\s+(your\s+)?(rules?|guidelines?|ethics?))/gi,
  },
];

export class InputSanitizer {
  private readonly patterns: SanitizePattern[];
  private readonly blockEnabled: boolean;

  constructor(
    extraPatterns: SanitizePattern[] = [],
    blockEnabled = true
  ) {
    this.patterns = [...BUILT_IN_PATTERNS, ...extraPatterns];
    this.blockEnabled = blockEnabled;
  }

  scan(text: string): SanitizeResult {
    for (const { name, severity, pattern } of this.patterns) {
      const match = pattern.exec(text);
      if (match) {
        return {
          safe: false,
          patternName: name,
          severity,
          matchedText: match[0].slice(0, 100),
        };
      }
    }
    return { safe: true };
  }

  /**
   * Convenience: scan and throw a structured error if blocked.
   * Returns cleaned text on success (strips NUL bytes, control chars).
   */
  sanitize(text: string): string {
    // Strip NUL bytes and control chars (preserve tab, LF, CR)
    const cleaned = text
      .replace(/\x00/g, "")
      .replace(/[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");

    const result = this.scan(cleaned);
    if (!result.safe && result.severity === "block" && this.blockEnabled) {
      throw new InjectionBlockedError(result.patternName ?? "unknown", result.matchedText ?? "");
    }
    return cleaned.trim();
  }
}

export class InjectionBlockedError extends Error {
  constructor(
    public readonly patternName: string,
    public readonly matchedText: string
  ) {
    super(`Input blocked by injection scanner: pattern="${patternName}"`);
    this.name = "InjectionBlockedError";
  }
}
```

**Config:**
```yaml
security:
  inputSanitizer:
    enabled: false    # opt-in only — no change for existing operators
    blockEnabled: true
```

**Integration point:**
```typescript
// In the incoming message handler, before adding to session context:
if (gateway.config.security?.inputSanitizer?.enabled) {
  try {
    incomingText = inputSanitizer.sanitize(incomingText);
  } catch (err) {
    if (err instanceof InjectionBlockedError) {
      logger.warn(`[InputSanitizer] Blocked message from ${sender}: ${err.patternName}`);
      // Return a safe canned response to the sender
      return sendSafeRejection(sender, channel);
    }
    throw err;
  }
}
```

### PR scope estimate
- ~130–160 lines (new sanitizer file + ~20-line integration)
- No new dependencies
- **Opt-in only** — completely invisible to operators who don't enable it, zero risk of regression

---

## Submission Strategy Recommendations

**Before opening any PR:**
1. Go to OpenClaw Discord (`discord.gg/clawd`) in `#contributors` or `#security` channel
2. Present the problem description (Section 1 of each proposal) WITHOUT the code
3. Ask: "Is this a known issue? Is there a tracking issue or design doc? Would a PR for X be welcome?"
4. Wait for a maintainer to confirm direction before writing any code

**Sequence (if Discord confirms interest):**
- **First PR**: Proposal 1 (Pluggable Embedding) — most aligned with their local-first values; clean boundary; no risk of regression
- **Second PR** (after first merged or at least reviewed): Proposal 3 (Input Sanitizer) — opt-in only; simplest possible scope
- **Third PR** (last, most complex): Proposal 2 (DirectiveGuard) — touches the completion pipeline; needs more alignment first

**Never submit all three in one PR or in rapid sequence.**

---

## What We Are NOT Proposing to OpenClaw Core

Things we built for Sigrid that would NOT be appropriate for OpenClaw core:
- Our full Vörðr truth-verification pipeline — too domain-specific
- The `MemoryConsolidator` cron job — too application-level
- The Norse vocabulary and persona system — clearly belongs in ClawHub skills only
- The `SessionFileGuard` for session file integrity — our session files are custom to Sigrid; OpenClaw doesn't have the same attack surface

These belong either in our skill or as a ClawHub skill package, not in core.

---

## Notes on Code Style for OpenClaw

When actually writing the code for any PR:
- **TypeScript strict mode** — the project uses it
- **No `any` types** where avoidable
- **`async/await`** over Promise chains
- **Error classes** with `.name` set (not just `new Error()`)
- **Conventional commit** in PR title: `feat(security):` or `fix(memory):`
- **American English** in comments and error messages (not British)
- **JSDoc** for public interfaces/methods
- **`pnpm`** for package management
- **Node 24** target (Node 22.16+ compatible)
- **`fetch` API** — built-in in Node 24, no need for `axios` or `node-fetch`
- Test framework: check their `package.json` for the test runner (likely `vitest` or `jest`) — match it exactly
