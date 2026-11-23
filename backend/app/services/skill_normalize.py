"""
Skill-name normalisation and matching that works for skills nobody listed.

Two names are "the same skill" when they differ only by case, punctuation,
spacing, a trailing "js", a plural "s", or a vendor prefix:
    Node.js = NodeJS = node js        Postgres ~ PostgreSQL (fuzzy)
    Microsoft Excel = Excel           Google Analytics 4 ~ Google Analytics
Deliberately NOT the same: React / Redux, Java / JavaScript, SQL / MySQL.
"""

import re
from difflib import SequenceMatcher

_VENDOR_PREFIXES = {"microsoft", "ms", "google", "amazon", "apache", "ibm", "oracle", "the"}


def _tokens(name: str) -> list:
    text = re.sub(r"\(.*?\)", " ", name.lower())
    return [t for t in re.split(r"[^a-z0-9+#]+", text) if t]


def _squash(tokens) -> str:
    key = "".join(tokens)

    # plural / "s" ending: "APIs" == "API"
    if len(key) > 4 and key.endswith("s") and not key.endswith("ss"):
        key = key[:-1]

    return key


def skill_keys(name: str) -> set:
    """Comparable keys for a skill name (usually 1-4 of them)."""

    tokens = _tokens(name)

    if not tokens:
        return set()

    variants = [tokens]

    stripped = [t for t in tokens if t not in _VENDOR_PREFIXES]

    if stripped and stripped != tokens:
        variants.append(stripped)

    keys = set()

    for variant in variants:

        key = _squash(variant)

        keys.add(key)

        # "Express.js" / "ExpressJS" / "Express"
        if len(key) > 4 and key.endswith("js"):
            keys.add(key[:-2])

    return {k for k in keys if k}


def skill_key(name: str) -> str:
    """One stable key (the first variant), handy for evaluation and dedupe."""

    return _squash(_tokens(name))


def is_same_skill(a: str, b: str) -> bool:
    """Equivalent names: same after normalisation, or a close spelling variant."""

    keys_a, keys_b = skill_keys(a), skill_keys(b)

    if keys_a & keys_b:
        return True

    # Spelling variants: "Postgres" ~ "PostgreSQL", "Kubernates" ~ "Kubernetes".
    # Lengths must be close so "Machine Learning" never merges with
    # "Azure Machine Learning".
    for x in keys_a:
        for y in keys_b:

            if (
                min(len(x), len(y)) >= 6
                and abs(len(x) - len(y)) <= 3
                and SequenceMatcher(None, x, y).ratio() >= 0.82
            ):
                return True

    return False


def satisfies(have: str, need: str) -> bool:
    """
    Does a skill the candidate has satisfy a skill the job needs?
    Same skill, or the candidate's is MORE specific ("Google Analytics 4"
    satisfies "Google Analytics"). Never the other way round: "Machine Learning"
    does not satisfy "Azure Machine Learning".
    """

    if is_same_skill(have, need):
        return True

    need_tokens = [t for t in _tokens(need) if t not in _VENDOR_PREFIXES]
    have_tokens = [t for t in _tokens(have) if t not in _VENDOR_PREFIXES]

    if need_tokens and set(need_tokens) <= set(have_tokens) and len(have_tokens) - len(need_tokens) <= 2:

        return len(need_tokens) >= 2 or len("".join(need_tokens)) >= 6

    return False


def matches_any(skill: str, others) -> bool:
    return any(is_same_skill(skill, other) for other in others)


def satisfied_by_any(need: str, have_skills) -> bool:
    return any(satisfies(have, need) for have in have_skills)


def dedupe_skills(skills) -> list:
    """Remove equivalent names, keeping the first spelling seen."""

    kept = []

    for skill in skills:
        if not matches_any(skill, kept):
            kept.append(skill)

    return kept
