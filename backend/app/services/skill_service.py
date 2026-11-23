import contextvars
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor

from langsmith import traceable

# Registers the extra skills; must be imported before patterns are compiled.
from backend.app.core import skills_extended
from backend.app.core.skills import (
    SKILL_ALIASES,
    SKILL_DISPLAY_NAMES,
    TECH_SKILLS,
)
from backend.app.core.skills_extended import (
    BROAD_CREDIT,
    BROAD_GROUPS,
    CASE_SENSITIVE_PATTERNS,
    SKILL_IMPLIES,
    TIGHT_CREDIT,
    TIGHT_GROUPS,
)
from backend.app.services.skill_mining import mine_skills
from backend.app.services.skill_normalize import dedupe_skills, satisfied_by_any

logger = logging.getLogger(__name__)

# A skill only matches when it is not glued to other word characters or to
# "+" / "#". The old "\b...\b" pattern could never match skills ending in a
# symbol, such as "c++".
_BEFORE = r"(?<![\w+#])"
_AFTER = r"(?![\w+#])"


def _compile_pattern(skill: str) -> re.Pattern:

    # Ordinary English words (express, excel, tally, jest ...) only count in
    # their exact capitalised form.
    if skill in CASE_SENSITIVE_PATTERNS:
        return re.compile(CASE_SENSITIVE_PATTERNS[skill])

    # A single letter is only a skill when written as a capital "C"
    # (otherwise "(c)" or "plan c" would count as the C language).
    if skill == "c":
        return re.compile(r"(?<![\w+#.\-])C(?![\w+#\-])")

    names = sorted(
        [skill, *SKILL_ALIASES.get(skill, [])],
        key=len,
        reverse=True
    )

    alternatives = "|".join(re.escape(name) for name in names)

    return re.compile(
        _BEFORE + "(?:" + alternatives + ")" + _AFTER,
        re.IGNORECASE
    )


_SKILL_PATTERNS = {
    skill: _compile_pattern(skill)
    for skill in TECH_SKILLS
}

_DISPLAY = {
    skill: SKILL_DISPLAY_NAMES.get(skill, skill.title())
    for skill in TECH_SKILLS
}

_KEY_BY_DISPLAY = {display: key for key, display in _DISPLAY.items()}


def normalize_text(text: str) -> str:
    # PDF extraction often breaks multi-word skills across lines
    # ("machine\nlearning"), so collapse all whitespace.
    return re.sub(r"\s+", " ", text)


# ------------------------------------------------------------------ extraction
def extract_skills(text: str):
    """Vocabulary-only extraction: fast, precise, canonical names."""

    text = normalize_text(text)

    extracted = set()

    for skill, pattern in _SKILL_PATTERNS.items():

        if pattern.search(text):
            extracted.add(_DISPLAY[skill])

    return sorted(extracted)


def _covered_by_vocab(name: str) -> bool:
    """True if a candidate contains a vocabulary skill ("LLM APIs" contains
    "LLM"; "Retrieval-Augmented Generation" is an alias of "RAG"). The
    vocabulary entry already represents it, so keeping both would double count."""

    text = normalize_text(name)

    return any(pattern.search(text) for pattern in _SKILL_PATTERNS.values())


def extract_skills_rules(text: str):
    """Vocabulary + rule-based mining (no LLM, fully deterministic)."""

    mined = [m for m in mine_skills(text) if not _covered_by_vocab(m)]

    return dedupe_skills([*extract_skills(text), *mined])


def extraction_mode() -> str:
    """'rules' (offline, deterministic) or 'hybrid' (rules + verified LLM)."""

    mode = os.getenv("SKILL_EXTRACTION_MODE")

    if not mode:
        try:
            from backend.app.core.config import settings
            mode = getattr(settings, "SKILL_EXTRACTION_MODE", "hybrid")
        except Exception:
            mode = "hybrid"

    return "rules" if str(mode).strip().lower() == "rules" else "hybrid"


def extract_document_skills(text: str, use_llm=None) -> list:
    """
    All skills in a document. Vocabulary names win (canonical spelling), then
    LLM-verified skills, then rule-mined ones; near-duplicates are merged.
    """

    if use_llm is None:
        use_llm = extraction_mode() == "hybrid"

    vocab = extract_skills(text)

    mined = [m for m in mine_skills(text) if not _covered_by_vocab(m)]

    llm_skills = []

    if use_llm:
        from backend.app.services.skill_llm import extract_with_llm
        llm_skills = [s for s in extract_with_llm(text) if not _covered_by_vocab(s)]

    return dedupe_skills([*vocab, *llm_skills, *mined])


# ------------------------------------------------------------------ relations
def implied_skills(skills) -> set:
    """
    The skills plus everything they imply (GitHub -> Git, ChromaDB ->
    Vector Database, MySQL -> SQL ...). Skills the vocabulary does not know are
    kept as they are. Used for matching and grounding; never shown as
    "what the resume says".
    """

    skills = set(skills)

    keys = {_KEY_BY_DISPLAY[s] for s in skills if s in _KEY_BY_DISPLAY}

    changed = True

    while changed:
        changed = False

        for key in list(keys):
            for implied in SKILL_IMPLIES.get(key, []):
                if implied not in keys:
                    keys.add(implied)
                    changed = True

    return skills | {_DISPLAY[key] for key in keys if key in _DISPLAY}


def find_related_skills(missing_skills, owned_skills) -> list:
    """
    For each missing JD skill, look for a related skill the candidate does have.
    Returns [{"skill", "credit", "via"}] for the missing skills that earn
    partial credit. Only skills the vocabulary knows can be related; an unknown
    skill is either matched or missing, never half-credited.
    """

    owned_keys = {_KEY_BY_DISPLAY[s] for s in owned_skills if s in _KEY_BY_DISPLAY}

    related = []

    for skill in missing_skills:

        key = _KEY_BY_DISPLAY.get(skill)

        if key is None:
            continue

        best_credit, best_via = 0.0, None

        for groups, credit in ((TIGHT_GROUPS, TIGHT_CREDIT), (BROAD_GROUPS, BROAD_CREDIT)):

            for group in groups:

                if key not in group:
                    continue

                shared = sorted((group & owned_keys) - {key})

                if shared and credit > best_credit:
                    best_credit, best_via = credit, _DISPLAY[shared[0]]

        if best_via:
            related.append({
                "skill": skill,
                "credit": best_credit,
                "via": best_via
            })

    return related


# ------------------------------------------------------------------ matching
def _extract_both(resume_text: str, jd_text: str):
    """Extract both documents; with the LLM layer the two calls run in parallel."""

    if extraction_mode() == "rules":
        return (
            extract_document_skills(resume_text, use_llm=False),
            extract_document_skills(jd_text, use_llm=False),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:

        # copy_context keeps the LangSmith trace parent inside the worker threads
        resume_future = pool.submit(
            contextvars.copy_context().run, extract_document_skills, resume_text, True
        )
        jd_future = pool.submit(
            contextvars.copy_context().run, extract_document_skills, jd_text, True
        )

        return resume_future.result(), jd_future.result()


@traceable(name="extract_and_match_skills", run_type="tool")
def extract_and_match_skills(
    resume_text: str,
    jd_text: str
):

    resume_skills, jd_skills = _extract_both(resume_text, jd_text)

    # Matching also counts skills that the resume's skills imply, and treats
    # spelling variants (Postgres / PostgreSQL) as the same skill.
    effective_skills = implied_skills(resume_skills)

    matched_skills = sorted(
        skill for skill in jd_skills if satisfied_by_any(skill, effective_skills)
    )

    missing_skills = sorted(
        skill for skill in jd_skills if skill not in matched_skills
    )

    related_skills = find_related_skills(
        missing_skills,
        effective_skills
    )

    return {
        "resume_skills": sorted(resume_skills),
        "jd_skills": sorted(jd_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "related_skills": related_skills
    }
