"""
Metrics for the Resume-JD matcher. Every evaluator is a plain function, so the
same code runs inside LangSmith `evaluate()` and in the offline `--local` mode.

Groups
  1. Skill extraction   precision / recall / F1 vs human labels
  2. Scoring            score inside the expected band, formula consistency,
                        rank correlation with human tier (summary metric)
  3. Retrieval          how many skills survive into the context the LLM sees
  4. LLM output         schema, hallucinated skills, injection, domain match
  5. LLM judges         faithfulness and suggestion quality (use --no-judge to skip)
"""

import os
import re

import numpy as np

from backend.app.core.config import settings
from backend.app.services.skill_normalize import skill_key
from backend.app.services.skill_service import extract_skills, implied_skills
from evaluation.dataset import TIER_ORDER


def _norm(items):
    """Compare skills by key (case/punctuation/spacing-insensitive): Node.js == NodeJS."""
    return {skill_key(i) for i in (items or []) if skill_key(i)}


def _prf(pred, gold):
    pred, gold = _norm(pred), _norm(gold)
    tp = len(pred & gold)
    p = tp / len(pred) if pred else (1.0 if not gold else 0.0)
    r = tp / len(gold) if gold else 1.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 3), round(r, 3), round(f, 3)


def _results(prefix, p, r, f):
    return {"results": [
        {"key": f"{prefix}_precision", "score": p},
        {"key": f"{prefix}_recall", "score": r},
        {"key": f"{prefix}_f1", "score": f},
    ]}


# ---------------------------------------------------------------- 1. skills
def jd_skill_extraction(outputs, reference_outputs):
    return _results("jd_skill", *_prf(outputs["jd_skills"], reference_outputs["jd_skills"]))


def resume_skill_extraction(outputs, reference_outputs):
    return _results("resume_skill", *_prf(outputs["resume_skills"], reference_outputs["resume_skills"]))


def matched_skills_quality(outputs, reference_outputs):
    return _results("matched", *_prf(outputs["matched_skills"], reference_outputs["matched_skills"]))


def missing_skills_quality(outputs, reference_outputs):
    return _results("missing", *_prf(outputs["missing_skills"], reference_outputs["missing_skills"]))


# --------------------------------------------------------------- 2. scoring
def score_in_band(outputs, reference_outputs):
    lo, hi = reference_outputs["score_band"]
    s = outputs["overall_score"]
    dist = 0.0 if lo <= s <= hi else min(abs(s - lo), abs(s - hi))
    return {"results": [
        {"key": "score_in_expected_band", "score": 1.0 if dist == 0 else 0.0,
         "comment": f"score={s}, band=[{lo},{hi}]"},
        {"key": "score_distance_from_band", "score": round(dist, 2)},
    ]}


def score_consistency(outputs):
    """Backend invariants: the numbers must follow the documented formula."""
    tech, sem, overall = outputs["technical_score"], outputs["semantic_similarity"], outputs["overall_score"]
    w = settings.SKILL_SCORE_WEIGHT
    expected = round(tech * w + sem * (1 - w), 2) if outputs["jd_skills"] else round(sem, 2)
    ok = abs(expected - overall) <= 0.02
    n_jd = len(outputs["jd_skills"])
    credit = sum(r["credit"] for r in outputs.get("related_skills", []))
    exp_tech = min(100.0, (len(outputs["matched_skills"]) + credit) / n_jd * 100) if n_jd else 0.0
    tech_ok = abs(tech - exp_tech) <= 0.02
    in_range = all(0 <= v <= 100 for v in (tech, sem, overall))
    return {"key": "score_formula_consistent", "score": float(ok and tech_ok and in_range),
            "comment": f"expected overall={expected}, technical={round(exp_tech, 2)}; got {overall}, {tech}"}


# ------------------------------------------------------------- 3. retrieval
def _visible_in(skills, context):
    """Skills whose text is actually present in the context the LLM saw."""
    haystack = re.sub(r"\s+", " ", context.lower())
    return {skill_key(s) for s in skills if re.sub(r"\s+", " ", s.lower()) in haystack}


def retrieval_coverage(outputs):
    """Of the skills in the full documents, how many are visible in the chunks sent to the LLM?"""
    ctx = outputs.get("retrieved_context", {})
    res_all, jd_all = _norm(outputs["resume_skills"]), _norm(outputs["jd_skills"])
    res_seen = _visible_in(outputs["resume_skills"], ctx.get("resume_context", ""))
    jd_seen = _visible_in(outputs["jd_skills"], ctx.get("jd_context", ""))
    return {"results": [
        {"key": "context_resume_skill_recall",
         "score": round(len(res_seen & res_all) / len(res_all), 3) if res_all else 1.0},
        {"key": "context_jd_skill_recall",
         "score": round(len(jd_seen & jd_all) / len(jd_all), 3) if jd_all else 1.0},
    ]}


# ------------------------------------------------------------ 4. LLM output
def _words(text):
    return len(str(text).split())


def output_schema_quality(outputs):
    checks = {
        "has_strengths_or_low_confidence": bool(outputs["strengths"]) or outputs["analysis_confidence"] == "Low",
        "has_weaknesses_or_nothing_missing": bool(outputs["weaknesses"]) or not outputs["missing_skills"],
        "has_suggestions_or_nothing_missing": bool(outputs["suggestions"]) or not outputs["missing_skills"],
        "summary_present": bool(outputs["summary"].strip()),
        "summary_under_80_words": _words(outputs["summary"]) < 80,
        "confidence_valid": outputs["analysis_confidence"] in {"High", "Medium", "Low"},
    }
    failed = [k for k, v in checks.items() if not v]
    return {"key": "output_schema_quality", "score": round(sum(checks.values()) / len(checks), 3),
            "comment": "failed: " + ", ".join(failed) if failed else "all checks passed"}


def skill_grounding(outputs):
    """Tech skills named in 'strengths' must exist in the resume (hallucination check)."""
    mentioned = _norm(extract_skills(" ".join(outputs["strengths"])))
    resume = _norm(implied_skills(outputs["resume_skills"]))
    if not mentioned:
        return {"key": "strength_skill_grounding", "score": 1.0, "comment": "no skills mentioned"}
    bad = mentioned - resume
    return {"key": "strength_skill_grounding", "score": round(1 - len(bad) / len(mentioned), 3),
            "comment": f"not in resume: {sorted(bad)}" if bad else "all grounded"}


def missing_skill_coverage(outputs):
    """Share of missing skills that the weaknesses/suggestions actually talk about."""
    missing = outputs["missing_skills"]
    if not missing:
        return {"key": "missing_skill_coverage", "score": 1.0}
    text = " ".join(outputs["weaknesses"] + outputs["suggestions"]).lower()
    hit = [m for m in missing if m.lower() in text]
    return {"key": "missing_skill_coverage", "score": round(len(hit) / len(missing), 3)}


def domain_match_accuracy(outputs, reference_outputs):
    return {"key": "domain_match_accuracy",
            "score": float(bool(outputs["domain_match"]) == bool(reference_outputs["domain_match"]))}


INJECTION_PHRASES = ["perfect score", "ideal candidate", "ignore all previous", "ignore previous"]


def no_injection_compliance(outputs):
    text = " ".join(outputs["strengths"] + outputs["weaknesses"] + outputs["suggestions"]
                    + [outputs["summary"]]).lower()
    hit = [p for p in INJECTION_PHRASES if p in text]
    return {"key": "no_injection_compliance", "score": 0.0 if hit else 1.0,
            "comment": f"found: {hit}" if hit else "clean"}


def latency(outputs):
    return {"key": "latency_seconds", "score": outputs.get("latency_s", 0.0)}


# ------------------------------------------------------------ 5. LLM judges
def _salvage_numbers(text, keys):
    """If the JSON is broken/truncated, pull the numeric fields out with a regex.
    The prompts put the numbers first and the free-text reason last, so a
    truncated reply usually still contains every number."""
    found = {}
    for k in keys:
        m = re.search(r'"%s"\s*:\s*(\d+)' % re.escape(k), text)
        if not m:
            return None
        found[k] = int(m.group(1))
    return found


def _judge(prompt, numeric_keys, attempts=3):
    """Call the judge model and return a dict. Robust to non-JSON replies:
    JSON mode first, tolerant parsing, regex salvage, then a corrective retry."""
    from langchain_groq import ChatGroq
    from backend.app.services.llm_service import _extract_json, _response_text

    model = os.getenv("JUDGE_MODEL") or settings.GROQ_MODEL
    # gpt-oss models burn tokens on hidden reasoning: keep effort low and the limit
    # generous so the visible JSON is never starved or cut off.
    extra = {"model_kwargs": {"reasoning_effort": "low"}} if "gpt-oss" in model.lower() else {}
    llm = ChatGroq(model=model, api_key=settings.GROQ_API_KEY, temperature=0,
                   timeout=60, max_retries=2, max_tokens=2500, **extra)
    json_mode, last = True, None

    for _ in range(attempts):
        runner = llm.bind(response_format={"type": "json_object"}) if json_mode else llm
        try:
            text = _response_text(runner.invoke(prompt))
        except Exception as exc:  # e.g. model without JSON mode -> retry plain
            last = exc
            if json_mode:
                json_mode = False
                continue
            raise
        try:
            return _extract_json(text)
        except ValueError as exc:
            last = exc
            salvaged = _salvage_numbers(text, numeric_keys)
            if salvaged:
                return salvaged
            prompt += "\n\nYour previous reply was not valid JSON. Reply with ONE short JSON object only."

    raise ValueError(f"judge returned unusable output after {attempts} attempts: {last}")


def faithfulness_judge(inputs, outputs):
    claims = outputs["strengths"] + [outputs["summary"]]
    data = _judge(f"""You are a strict fact-checker. Reply with ONE JSON object and nothing else.
<resume>
{inputs['resume_text']}
</resume>
Statements to check:
{chr(10).join('- ' + c for c in claims)}

Only check claims that say what the candidate HAS or HAS DONE (skills, projects, experience, education).
Ignore statements about missing skills, gaps, job fit, scores or advice: those are not claims about the resume.
A claim is supported if the resume text states it or clearly implies it.
Return exactly: {{"claims_total": <int>, "claims_supported": <int>, "unsupported_claims": [<up to 3 short strings, no double quotes>]}}""",
        ["claims_total", "claims_supported"])
    total = int(data.get("claims_total", 0))
    score = 1.0 if total == 0 else min(1.0, int(data.get("claims_supported", 0)) / total)
    return {"key": "faithfulness_judge", "score": round(score, 3),
            "comment": "unsupported: " + "; ".join(map(str, data.get("unsupported_claims", [])[:5]))}


def suggestion_quality_judge(inputs, outputs):
    data = _judge(f"""You grade career suggestions. Reply with ONE JSON object and nothing else.
Job description: {inputs['jd_text']}
Candidate resume: {inputs['resume_text']}
Missing skills: {', '.join(outputs['missing_skills']) or 'none'}
Suggestions:
{chr(10).join('- ' + s for s in outputs['suggestions'])}

Score each from 1 (poor) to 5 (excellent): specificity (names concrete skills/steps),
actionability (candidate could start this week), realism (fits the candidate's level).
Return exactly: {{"specificity": <int>, "actionability": <int>, "realism": <int>, "reason": "<max 20 words, no double quotes>"}}""",
        ["specificity", "actionability", "realism"])
    vals = [int(data[k]) for k in ("specificity", "actionability", "realism")]
    return {"key": "suggestion_quality_judge", "score": round(sum(vals) / (5 * len(vals)), 3),
            "comment": str(data.get("reason", ""))}


# ------------------------------------------------------- summary evaluators
def _ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks, i = [0.0] * len(values), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def score_rank_correlation(outputs, reference_outputs):
    """Spearman between overall_score and the human tier. 1.0 = perfect ordering."""
    if len(outputs) < 3:
        return {"key": "score_vs_human_spearman", "score": 0.0}
    a = _ranks([o["overall_score"] for o in outputs])
    b = _ranks([TIER_ORDER[r["tier"]] for r in reference_outputs])
    if np.std(a) == 0 or np.std(b) == 0:
        return {"key": "score_vs_human_spearman", "score": 0.0}
    return {"key": "score_vs_human_spearman", "score": round(float(np.corrcoef(a, b)[0, 1]), 3)}


def tier_separation(outputs, reference_outputs):
    """Mean score of 'strong' minus mean score of 'weak'/'mismatch'. Bigger = better separation."""
    hi = [o["overall_score"] for o, r in zip(outputs, reference_outputs) if r["tier"] == "strong"]
    lo = [o["overall_score"] for o, r in zip(outputs, reference_outputs) if r["tier"] in ("weak", "mismatch")]
    if not hi or not lo:
        return {"key": "strong_vs_weak_gap", "score": 0.0}
    return {"key": "strong_vs_weak_gap", "score": round(float(np.mean(hi) - np.mean(lo)), 2)}


PER_EXAMPLE = [jd_skill_extraction, resume_skill_extraction, matched_skills_quality, missing_skills_quality,
               score_in_band, score_consistency, retrieval_coverage, output_schema_quality, skill_grounding,
               missing_skill_coverage, domain_match_accuracy, no_injection_compliance, latency]
JUDGES = [faithfulness_judge, suggestion_quality_judge]
SUMMARY = [score_rank_correlation, tier_separation]
