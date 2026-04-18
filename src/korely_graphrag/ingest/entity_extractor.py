"""Entity extraction — single LLM call per document, JSON-mode.

Strips Korely-specific bits (multi-user tier routing, LLMContext tracking,
existing-entity vocabulary). The core prompt and quality gates are preserved.
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import dataclass

from ..config import get_settings
from ..providers.base import BaseProvider, get_provider

logger = logging.getLogger(__name__)


SUPPORTED_ENTITY_TYPES = frozenset({
    "person",
    "organization",
    "technology",
    "concept",
    "location",
    "topic",
    "fact",
    "decision",
    "evidence",
    "reasoning",
    "action_item",
})

_ENTITY_TYPE_ALIASES = {"action": "action_item"}

# Generic terms that create hairball hub-nodes if allowed in the graph.
# Bilingual (EN + IT) — Gemini handles either input language fine.
_GENERIC_BLACKLIST = frozenset({
    # English
    "technology", "economy", "science", "history", "politics", "art",
    "system", "data", "analysis", "development", "work", "performance",
    "artificial intelligence", "ai", "ml", "machine learning",
    "management", "communication", "information", "process", "strategy",
    "project", "research", "education", "culture", "society", "environment",
    "innovation", "business", "software", "engineering", "design",
    # Italian
    "tecnologia", "economia", "scienza", "storia", "politica", "arte",
    "sistema", "dati", "analisi", "sviluppo", "lavoro",
    "intelligenza artificiale", "ia", "comunicazione", "gestione",
    "innovazione", "informazione", "processo", "strategia", "progetto",
    "ricerca", "educazione", "cultura", "societa", "ambiente",
})

_VOWELS = set("aeiouAEIOUàèéìòùÀÈÉÌÒÙäëïöüÄËÏÖÜ")


@dataclass
class ExtractedEntity:
    name: str
    raw_name: str
    entity_type: str
    context: str = ""
    importance: float = 0.5


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_entity_name(name: str) -> str:
    if not name:
        return ""
    s = unicodedata.normalize("NFC", name.strip())
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u201C", '"').replace("\u201D", '"'))
    if not s:
        return ""

    # Strip leading articles (EN: The/A/An, IT: Il/Lo/La/I/Gli/Le/L')
    s = re.sub(
        r"^(?:l'\s*|il\s+|lo\s+|la\s+|i\s+|gli\s+|le\s+|the\s+|an?\s+)",
        "", s, count=1, flags=re.IGNORECASE,
    ).strip() or s

    # Acronyms (≤5 chars all-caps): keep as-is
    if len(s) <= 5 and s.upper() == s:
        return s
    # Preserve internal capitalization (PostgreSQL, GraphQL)
    if any(c.isupper() for c in s[1:]):
        return s
    return s.capitalize()


def is_valid_entity_name(name: str) -> bool:
    """Reject gibberish (asdasd, xxx, single chars). Zero false positives on real names."""
    name = (name or "").strip()
    if len(name) < 2:
        return False
    if len(name) <= 4 and name.upper() == name:
        return True  # short acronyms (AI, DB, USA, JWT)
    if not any(c in _VOWELS for c in name):
        return False

    cleaned = name.lower().replace(" ", "")
    if len(cleaned) > 3:
        if len(set(cleaned)) / len(cleaned) < 0.5:
            return False  # "aaaa", "ababab"
        for sub_len in range(2, len(cleaned) // 2 + 1):
            sub = cleaned[:sub_len]
            reps = len(cleaned) // sub_len
            if reps >= 2 and sub * reps == cleaned[: sub_len * reps] and len(cleaned) % sub_len == 0:
                return False  # "asdasd"
    return True


def should_index_content(text: str) -> bool:
    if not text:
        return False
    words = text.split()
    if len(words) < 30:
        return False
    if len(set(w.lower() for w in words)) / len(words) < 0.3:
        return False
    return True


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


_SYSTEM_PROMPT = "You extract entities from text and return them as a JSON object. Never invent information not present in the text."

_USER_PROMPT_TEMPLATE = """Analyze the following document and extract the most important entities ACTUALLY PRESENT in the text. Never invent.

DOCUMENT:
\"\"\"{text}\"\"\"

Extract up to {max_entities} entities. Prefer SPECIFIC and CONCRETE entities over generic ones.

ENTITY TYPES:
- person: named people, specific roles
- organization: companies, teams, departments, institutions
- technology: languages, frameworks, tools, databases, APIs
- concept: specific abstract themes, methodologies, patterns
- location: geographic places (cities, regions, countries, buildings)
- topic: 1-2 specific cross-cutting themes that link documents on the same precise subject
- fact: verifiable claims with numeric data or dates
- decision: explicitly stated decisions
- evidence: supporting data or proof
- reasoning: chains of reasoning, rationale
- action_item: concrete actions to perform

RULES:
1. Extract concrete entities FIRST (person, location, organization, technology), THEN add 1-2 SPECIFIC topics.
2. Topics must be CROSS-CUTTING but SPECIFIC. They should identify a precise sub-subject, not a whole category.
   GOOD: "Personalized PageRank", "Knowledge Graph Pruning", "Spaced Repetition", "Supply Chain Optimization"
   BAD (NEVER USE): "Technology", "Economy", "Science", "History", "AI", "Data", "System", "Politics", "Art"
   Rule: if the topic could apply to >30% of a typical user's documents, it is TOO generic.
3. Better 5 specific entities than 15 generic ones. Specificity beats coverage.
4. CANONICAL NAMES: always use the shortest, most universally recognized form.
   - If a known acronym exists, use the acronym (not the full form)
   - If the text introduces an acronym in parentheses (e.g. "Model Context Protocol (MCP)"), use the acronym
   - Do NOT invent variants with product prefixes, numbers, or modifiers

Return STRICT JSON in this shape (no prose, no markdown fence):
{{
  "entities": [
    {{"name": "...", "type": "...", "context": "max 100 chars", "importance": 0.0-1.0}},
    ...
  ]
}}
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sanitize_json_string(raw: str) -> str:
    raw = unicodedata.normalize("NFC", raw)
    repl = {
        "\u2018": "'", "\u2019": "'", "\u201C": '"', "\u201D": '"',
        "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00A0": " ",
    }
    for k, v in repl.items():
        raw = raw.replace(k, v)
    return raw


def _strip_code_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        # Remove leading fence (```json or ```) and trailing ```
        raw = re.sub(r"^```[a-zA-Z]*\n", "", raw)
        raw = re.sub(r"\n```\s*$", "", raw)
    return raw.strip()


def _repair_truncated_json(raw: str) -> str | None:
    last = raw.rfind("}")
    if last < 0:
        return None
    truncated = raw[: last + 1]
    open_brackets = truncated.count("[") - truncated.count("]")
    open_braces = truncated.count("{") - truncated.count("}")
    truncated = truncated.rstrip().rstrip(",") + "]" * open_brackets + "}" * open_braces
    try:
        json.loads(truncated)
        return truncated
    except json.JSONDecodeError:
        return None


def _deduplicate(raw_entities: list[dict]) -> list[dict]:
    by_name: dict[str, dict] = {}
    for ent in raw_entities:
        raw_name = str(ent.get("name") or "").strip()
        if not raw_name:
            continue
        norm = normalize_entity_name(raw_name)
        if not norm:
            continue
        importance = float(ent.get("importance", 0.5) or 0.5)
        existing = by_name.get(norm)
        if not existing or importance > float(existing.get("importance", 0.0)):
            ent_copy = dict(ent)
            ent_copy["name"] = norm
            ent_copy["raw_name"] = raw_name
            ent_copy["importance"] = importance
            by_name[norm] = ent_copy
    return list(by_name.values())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_entities_from_text(
    text: str,
    *,
    max_entities: int | None = None,
    provider: BaseProvider | None = None,
) -> list[ExtractedEntity]:
    """Single LLM call per document. Returns [] on any failure (never raises)."""
    text = (text or "").strip()
    if not text:
        return []

    settings = get_settings()
    max_entities = max_entities or settings.max_entities_per_doc
    min_importance = settings.min_entity_importance
    provider = provider or get_provider()

    trimmed = text[:10_000]
    user_prompt = _USER_PROMPT_TEMPLATE.format(text=trimmed, max_entities=max_entities)

    try:
        result = provider.complete(
            system=_SYSTEM_PROMPT,
            user=user_prompt,
            max_tokens=8192,
            temperature=0.2,
            json_mode=True,
        )
    except Exception as e:
        logger.error("[entity_extractor] LLM call failed: %s", e)
        return []

    raw = (result.text or "").strip()
    if not raw:
        return []

    raw = _strip_code_fence(raw)
    raw = _sanitize_json_string(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw)
        if not repaired:
            logger.warning("[entity_extractor] could not parse LLM JSON; first 200 chars: %r", raw[:200])
            return []
        data = json.loads(repaired)
        logger.info("[entity_extractor] repaired truncated JSON")

    raw_entities = data.get("entities") if isinstance(data, dict) else None
    if not isinstance(raw_entities, list):
        return []

    entities: list[ExtractedEntity] = []
    for ent in _deduplicate(raw_entities):
        name = ent.get("name") or ""
        etype = (ent.get("type") or ent.get("entity_type") or "concept").lower()
        etype = _ENTITY_TYPE_ALIASES.get(etype, etype)
        if etype not in SUPPORTED_ENTITY_TYPES:
            etype = "concept"
        importance = max(0.0, min(1.0, float(ent.get("importance", 0.5) or 0.5)))
        entities.append(ExtractedEntity(
            name=name,
            raw_name=ent.get("raw_name") or name,
            entity_type=etype,
            context=(ent.get("context") or "")[:200],
            importance=importance,
        ))

    # Quality gates
    entities = entities[:max_entities]
    entities = [e for e in entities if e.importance >= min_importance]
    entities = [e for e in entities if is_valid_entity_name(e.name)]
    entities = [e for e in entities if e.name.strip().lower() not in _GENERIC_BLACKLIST]

    logger.info(
        "[entity_extractor] extracted %d entities (prompt_tokens=%d, completion_tokens=%d)",
        len(entities), result.prompt_tokens, result.completion_tokens,
    )
    return entities


__all__ = [
    "ExtractedEntity",
    "extract_entities_from_text",
    "normalize_entity_name",
    "is_valid_entity_name",
    "should_index_content",
    "SUPPORTED_ENTITY_TYPES",
]
