# Evaluation (LangSmith)

Run from the project root (folder containing `backend/`):

    pip install -r requirements.txt
    python -m evaluation.run_eval --local        # offline table, no LangSmith needed
    python -m evaluation.run_eval                # LangSmith experiment
    python -m evaluation.run_eval --sync         # re-upload dataset after editing dataset.py

Add to `.env`:

    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY=...
    LANGSMITH_PROJECT=resume-jd-matcher
    JUDGE_MODEL=<a different Groq model than GROQ_MODEL>   # optional, avoids self-preference

## Metrics
| Group | Keys | Meaning |
|---|---|---|
| Skill extraction | jd/resume/matched/missing `_precision/_recall/_f1` | extractor vs human labels |
| Scoring | score_in_expected_band, score_distance_from_band, score_formula_consistent | sanity of the numbers |
| Dataset-level | score_vs_human_spearman, strong_vs_weak_gap | does the score rank candidates like a human? |
| Retrieval | context_resume_skill_recall, context_jd_skill_recall | skills visible to the LLM |
| LLM output | output_schema_quality, strength_skill_grounding, missing_skill_coverage, domain_match_accuracy, no_injection_compliance | |
| Judges | faithfulness_judge, suggestion_quality_judge | LLM-as-judge |
| Ops | latency_seconds (tokens/cost come from the trace) | |

Compare experiments in LangSmith after each change (chunk size, weights, prompt, model, skills list).
The dataset is small and synthetic; score bands are first guesses. Add real, anonymised, consented cases.
