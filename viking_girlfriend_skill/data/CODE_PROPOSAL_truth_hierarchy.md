# CODE PROPOSAL: Truth Hierarchy & Tiered Retrieval
# Date: 2026-03-20
# Author: Runa Gridweaver (AI)

This document contains the proposed Python code structures to implement the Truth Hierarchy in `mimir_well.py` and `vordur.py`.

## 1. Mímir's Well: Data Classification Enums

```python
from enum import Enum, IntEnum

class DataRealm(Enum):
    """The Nine Worlds of Data classification."""
    ASGARD = "asgard"           # Core Axioms / Identity
    MIDGARD = "midgard"         # Historical / General Facts
    VANAHEIM = "vanaheim"       # Speculative / Vibe / Intuition
    SVARTALFHEIM = "svartalfheim" # Code / Technical / Procedure
    JOTUNHEIM = "jotunheim"     # External / User Input / Unverified
    HEL = "hel"                 # Banned / Hallucination Patterns

class TruthTier(IntEnum):
    """The Roots of Yggdrasil hierarchy of authority."""
    DEEP_ROOT = 1    # Primary Sources (Eddas, Sagas, Core Laws)
    TRUNK = 2        # Secondary Sources (Hand-crafted Knowledge)
    BRANCH = 3       # Tertiary Sources (AI-generated, Scraped)
```

## 2. Updated KnowledgeChunk Dataclass

```python
@dataclass(slots=True)
class KnowledgeChunk:
    """A single knowledge unit with hierarchical metadata."""
    chunk_id: str
    text: str
    source_file: str
    domain: str
    realm: DataRealm    # Added for V2
    tier: TruthTier     # Added for V2
    level: int          # Legacy (1=raw, 2=cluster, 3=axiom)
    metadata: Dict[str, Any]
```

## 3. Tiered Retrieval Logic (Pseudocode)

```python
def retrieve(self, query: str, min_tier: TruthTier = TruthTier.BRANCH) -> List[KnowledgeChunk]:
    """Retrieve chunks, enforcing the Law of the Roots."""
    raw_results = self.chroma.search(query)
    
    # 1. Filter by minimum required tier
    filtered = [c for c in raw_results if c.tier <= min_tier]
    
    # 2. Resolve Ginnungagap (Conflicts)
    # If two chunks cover the same fact but have different tiers,
    # the lower tier (stronger root) automatically wins.
    deduplicated = self._resolve_tier_conflicts(filtered)
    
    return deduplicated
```

## 4. Vörðr: Verification Modes

```python
class VerificationMode(Enum):
    """Modes of truth-checking rigor."""
    GUARDED = "guarded"     # Zero tolerance, Tier 1 only.
    IRONSWORN = "ironsworn" # High rigor, Tier 1 & 2.
    SEIÐR = "seiðr"         # Medium rigor, allows Tier 3.
    WANDERER = "wanderer"   # Low rigor, speed priority.

def get_thresholds(mode: VerificationMode) -> Tuple[float, float]:
    """Adjust NLI thresholds based on the trance mode."""
    mapping = {
        VerificationMode.GUARDED: (0.95, 0.85),
        VerificationMode.IRONSWORN: (0.90, 0.75),
        VerificationMode.SEIÐR: (0.75, 0.50),
        VerificationMode.WANDERER: (0.60, 0.30),
    }
    return mapping.get(mode, (0.90, 0.75))
```
