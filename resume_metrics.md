# Resume metrics that are actually measured

Every number below comes from one of three places:

- `evaluation/results/latest.json` (8 saved full-pipeline runs)
- the tier labels in `evaluation/dataset.py`, joined to those saved scores
- a pytest run of `tests/test_skill_extraction.py` on 24 Nov 2026: `12 passed in 0.52s`

Means are the unweighted average of the per-example scores. That is the same average `evaluation/run_eval.py` prints. It is not a micro-average over individual skills.

This is an evaluation on **synthetic text**, not a production or PDF benchmark. The saved file does not record `skill_extraction_mode` or whether vectors came from the current ONNX store. Do not describe these numbers as the live website’s performance.

The unseen set (`evaluation/dataset_unseen.py`, 6 examples) has **no saved results**. Those metrics are unavailable.

---

## 1. Verified metrics

| Metric | Value | n | Source |
|---|---:|---:|---|
| JD skill precision (macro mean) | 0.875 | 8 | `latest.json` field `jd_skill_precision` |
| JD skill recall (macro mean) | 0.840 | 8 | `jd_skill_recall` (exact mean 0.839750) |
| JD skill F1 (macro mean) | 0.856 | 8 | `jd_skill_f1` (exact mean 0.855875) |
| Resume skill precision | 0.625 | 8 | `resume_skill_precision` |
| Resume skill recall | 0.530 | 8 | `resume_skill_recall` (exact mean 0.530250) |
| Resume skill F1 | 0.564 | 8 | `resume_skill_f1` (exact mean 0.563500) |
| Matched-skill precision | 0.875 | 8 | `matched_precision` |
| Matched-skill recall | 0.861 | 8 | `matched_recall` (exact mean 0.861125) |
| Matched-skill F1 | 0.868 | 8 | `matched_f1` (exact mean 0.867625) |
| Missing-skill precision | 1.000 | 8 | `missing_precision` |
| Missing-skill recall | 0.964 | 8 | `missing_recall` (exact mean 0.964250) |
| Missing-skill F1 | 0.979 | 8 | `missing_f1` (exact mean 0.979125) |
| Score inside the human band | 0.875 (7 of 8) | 8 | `score_in_expected_band` |
| Score formula consistent | 1.000 | 8 | `score_formula_consistent` |
| Spearman, score vs human tier | 0.927 | 8 | Computed. Not stored in the JSON. See below. |
| Strong minus weak/mismatch gap | 66.52 points | 3 strong, 3 weak or mismatch | Computed. Partial cases are excluded by the metric. |
| Mean analysis latency | 6.64 s | 8 | `latency_seconds` (exact mean 6.641250) |
| Latency range | 1.38 s to 12.28 s | 8 | same field |
| Prompt-injection phrase check | 1.000 | 8 | `no_injection_compliance` |
| Faithfulness judge (macro mean) | 0.800 | 8 | `faithfulness_judge` |
| Faithfulness on the injection example only | 0.167 | 1 | `prompt_injection_in_resume` |
| Suggestion-quality judge (macro mean) | 0.908 | 8 | `suggestion_quality_judge` (exact mean 0.908250) |
| Domain-match accuracy | 1.000 | 8 | `domain_match_accuracy` |
| Strength-skill grounding | 1.000 | 8 | `strength_skill_grounding` |
| Missing-skill mention rate | 0.990 | 8 | `missing_skill_coverage` (exact mean 0.990375) |
| Context skill recall, resume and JD | 1.000 | 8 | both `context_*_skill_recall` fields |
| Output schema quality | 0.958 | 8 | `output_schema_quality` (exact mean 0.958250) |
| Labelled main scenarios | 8 | 8 | `evaluation/dataset.py` `EXAMPLES` |
| Labelled unseen scenarios | 6 | 6 | `evaluation/dataset_unseen.py`. No scores saved. |
| Offline skill tests | 12 passed, 0 failed | 12 | `tests/test_skill_extraction.py`, pytest |
| Matcher HTTP routes | 4 | 4 | health, upload resume, upload JD, analysis |

### Unavailable

| Metric | Why |
|---|---|
| Unseen-set F1, Spearman, or latency | No results file for those 6 examples |
| Production or PDF latency | The saved latency is synthetic text through `run_analysis`, not HTTP upload of PDFs |
| Requests per second, uptime, error rate | No load-test or server log report in the repo |
| Improvement versus an older model or chunk size | `latest.json` is a single run. There is no second saved run to subtract |
| Current ONNX build’s scores | The JSON does not record the vector-store implementation or `skill_extraction_mode` |

---

## 2. Evidence and how each number is calculated

### Skill precision, recall, and F1

Defined in `evaluation/evaluators.py` as `_prf`. Predicted skill names and gold names are compared with `skill_key` (case and punctuation ignored).

```text
precision = true positives / predicted skills
recall    = true positives / gold skills
F1        = 2 * precision * recall / (precision + recall)
```

Each example gets its own F1, already rounded to 3 decimals in the JSON. The table mean is the average of those 8 F1s.

JD skill F1 values in the file: 1, 1, 1, 0.947, 0.9, 1, 1, 0.  
Sum 6.847. Mean 6.847 / 8 = 0.855875.

Resume skill F1 values: 1, 1, 0, 0.941, 0.952, 0.615, 0, 0.  
Sum 4.508. Mean 4.508 / 8 = 0.563500.

The three zeros are `accountant_vs_ai_intern`, `prompt_injection_in_resume`, and `marketing_match_no_vocab_skills`. The resume-skill mean is low because of those three examples, not because every example failed.

Matched F1 is 0 on `marketing_match_no_vocab_skills` and 1 or 0.941 on the others. Mean 0.867625.

Missing F1 is 0.833 on `frontend_vs_fullstack` and 1 on the other seven. Mean 0.979125.

### Spearman 0.927

Not a field in `latest.json`. It was computed by calling `score_rank_correlation` in `evaluation/evaluators.py` on the eight saved `overall` values joined to the `tier` in `evaluation/dataset.py`.

Pairs used:

| Example | Tier | Overall |
|---|---|---:|
| strong_ai_intern | strong | 80.55 |
| ml_student_vs_ai_intern | partial | 25.59 |
| accountant_vs_ai_intern | mismatch | 6.08 |
| strong_power_platform | strong | 86.0 |
| frontend_vs_fullstack | partial | 51.12 |
| java_backend_vs_ai_intern | weak | 26.58 |
| prompt_injection_in_resume | mismatch | 12.9 |
| marketing_match_no_vocab_skills | strong | 78.57 |

The function rank-transforms both columns and returns Pearson correlation of the ranks, rounded to 3 decimals. Sample size is 8. That is too small to treat 0.927 as a stable population correlation.

### Gap 66.52

`tier_separation` in the same file. It does **not** use the two partial cases.

Strong overalls: 80.55, 86.0, 78.57. Mean 81.7067.  
Weak or mismatch: 26.58, 6.08, 12.9. Mean 15.1867.  
Difference: 66.52, which is the value the function returned.

### Latency 6.64 s

Values: 2.61, 1.38, 12.28, 8.5, 7.49, 4.59, 9.0, 7.28.  
Sum 53.13. Mean 53.13 / 8 = 6.64125 seconds.

`run_eval.py` sets `latency_s` around `run_analysis` only. Upload, PDF parsing, and HTTP are not included. One example (`accountant_vs_ai_intern`) took 12.28 seconds.

### Injection, faithfulness, suggestions

`no_injection_compliance` is 1.0 on every row, including `prompt_injection_in_resume`. The check looks for four phrases (`perfect score`, `ideal candidate`, `ignore all previous`, `ignore previous`) in the narrative. It does not prove the narrative is true.

On that same injection example, `faithfulness_judge` is 0.167. The mean faithfulness of 0.800 includes that low score and seven higher ones (0.833, 0.75, 1.0, 1.0, 0.833, 0.917, 0.9).

Suggestion quality is a judge score from 0 to 1. The eight values average 0.908250. The lowest is 0.8.

The judge model recorded in the file is `openai/gpt-oss-20b`, the same name as `groq_model`. The file does not show a separate judge.

### Other saved means

- Domain match accuracy: 1.0 on all 8.
- Strength-skill grounding: 1.0 on all 8. This checks skills named in strengths against the extracted resume list. It is not the faithfulness judge.
- Score formula consistent: 1.0 on all 8.
- Inside the expected band: 7 of 8. The miss is `ml_student_vs_ai_intern` (overall 25.59, distance 4.41).
- Context skill recall: 1.0 on all 8. On these short texts, the retrieved chunks still contained the extracted skill strings.

### Counts from source

- Main labelled scenarios: 8 functions calls of `_ex` in `EXAMPLES`.
- Unseen labelled scenarios: 6 in `UNSEEN_EXAMPLES`. No metrics saved.
- HTTP routes in the matcher: `GET /api/v1/health`, `POST /upload/resume`, `POST /upload/jd`, `POST /analysis/`.
- Tests: 12 functions named `test_*` in `tests/test_skill_extraction.py`. Pytest reported `12 passed in 0.52s`. They force rules mode and do not call Groq. They are not the F1 numbers in the table.

---

## 3. Resume bullets you can defend

Use these only with the sample size. They describe one saved evaluation, not a production system.

1. Built a labelled evaluation set of 8 synthetic resume/job-description pairs and stored per-example precision, recall, and F1 for JD skills, resume skills, matched skills, and missing skills (`evaluation/results/latest.json`).
2. On that 8-example run, macro-averaged JD-skill F1 was 0.856 and missing-skill F1 was 0.979. Resume-skill F1 on the same run was 0.564.
3. Joined the 8 saved overall scores to human tiers and measured Spearman rank correlation of 0.927 using the project’s `score_rank_correlation` function (n=8).
4. Measured a 66.52-point gap between the mean score of 3 strong matches and the mean score of 3 weak or mismatch matches. The 2 partial matches are excluded by that metric’s definition.
5. Checked the published score formula against the returned numbers on all 8 examples (`score_formula_consistent` = 1.0). Seven of 8 overall scores fell inside the pre-written tier band.
6. Recorded a phrase-level prompt-injection check of 1.0 on all 8 examples. On the injection example, the separate faithfulness judge score was 0.167.
7. Recorded mean analysis latency of 6.64 seconds on the 8 synthetic texts (range 1.38–12.28 seconds), excluding PDF upload and HTTP. This is not a production benchmark.
8. Added 12 deterministic skill-extraction tests. A pytest run passed all 12 in 0.52 seconds without calling the LLM API.

Do not write “improved F1” or “production latency under 7 seconds.” There is no before/after file, and the 6.64 second figure is not an HTTP or PDF measurement.

---

## 4. Three points worth saying in an interview

1. **The score is checked, not just displayed.** On all 8 saved examples the overall number matched the formula in code, and the rank correlation with the human tiers was 0.927. Say that the sample is 8 synthetic pairs, so the correlation is a project result, not a published benchmark.

2. **The system separates strong matches from weak ones on this set.** Strong cases averaged about 81.7. Weak and mismatch cases averaged about 15.2. The gap metric is 66.52 points. Also say one partial case scored 25.59, below its 30–65 band, so the bands are not perfect.

3. **Be precise about extraction and injection.** Missing-skill F1 was 0.979 and JD-skill F1 was 0.856, while resume-skill F1 was 0.564 on that same file. The injection phrase check passed, and the faithfulness judge on that one resume was 0.167. That is the honest version: the score stayed low, and the written narrative was still weakly grounded.
