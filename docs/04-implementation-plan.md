# 04 -- Implementation Plan

## Phases and Milestones

Each phase has a kill gate: if the gate condition is not met, the project stops or pivots before committing further resources.

### Phase 0: Foundation (Week 1-2)

**What:** Python package scaffold, task generation, subprocess sandbox, split-aware verifier, pass@k estimator, reward functions, mock trainer, analysis module, curriculum stubs, ledger dataclasses, notebook template, config system, preregistration documents.

**Kill gate:** `uv run python -m unittest discover -s tests -v` passes, `uv run python scripts/00_proposer_viability.py` runs end-to-end on toy tasks, and the mock proposer/solver produce sensible solve counts.

**Compute:** Laptop CPU. No GPU.

**Deliverables:**
- `src/frontier_delta/` package with all modules.
- `tests/` with passing tests for pass@k, verifier, rewards, ledger.
- `pyproject.toml`, `.python-version`, `uv.toml`, and `uv.lock` for the Python project workflow.
- `configs/base.yaml` and configs for all v1 arms named in the design.
- `prereg/protocol.md` and `prereg/holdout_manifest.example.json`.

### Phase 1: Proposer Viability (Week 3-4)

**What:** Replace mock proposer with a real frozen frontier model API call. Generate 100-500 program-induction tasks with varying difficulty. Measure task diversity (AST distance), held-out example coverage, and reference solution correctness.

**Kill gate:** At least 100 tasks pass checker-A verification (reference solution is correct on held-out examples), task diversity (AST distance) exceeds threshold, and no more than 5% of tasks have ambiguous specifications.

**Compute:** API credits for ~1M tokens. No GPU.

### Phase 2: Minimal Loop (Week 5-8)

**What:** Implement the full loop with a real small solver model (1-3B parameters) and LoRA fine-tuning via a library like `unsloth` or `peft`. Run one arm (vanilla RLVR) for 5 rounds on 100 tasks. Measure support-set change.

**Kill gate:** The loop runs without crashes for 5 rounds, support-set metrics are computable, and the system detects whether any tasks were gained. If zero tasks are gained after 5 rounds of vanilla RLVR, the project proceeds to test exploration-preserving arms (the null hypothesis may be true).

**Compute:** Single consumer GPU (RTX 3090/4090 or cloud equivalent), ~100 GPU-hours.

### Phase 3: Measurement Instrument (Week 9-12)

**What:** Run all control arms (random reward, format-only, no-frontier replay) and at least one treatment arm (exploration-preserving) for sufficient rounds to measure support-set change with statistical power. Implement checker-B audit with independent sandbox.

**Kill gate:** Control arms show no significant support-set expansion (confirming they are valid controls). At least one treatment arm shows measurable signal distinguishable from controls. If all arms (including controls) show expansion, the measurement instrument is broken. If no arm shows expansion, the hypothesis is falsified at this scale.

**Compute:** 200-500 GPU-hours on single GPU.

### Phase 4: Full Battery (Week 13-20)

**What:** Run all experimental arms (vanilla RLVR, prolonged RL, exploration-preserving, self-play, STaR/ReST, distillation, random reward, format-only, no-frontier replay, library frozen/shuffled/random) for 10-20 rounds each. Collect full support-set transfer maps.

**Kill gate:** At least one treatment arm shows statistically significant support-set expansion over controls (p < 0.01, Bonferroni-corrected). The pattern of gained/lost/sharpened tasks is interpretable and consistent with the arm's mechanism.

**Compute:** 500-2000 GPU-hours, potentially on multiple GPUs in parallel.

### Phase 5: Library / Transfer (Week 21-28)

**What:** Implement library learning (DreamCoder/LILO-style). Test whether a function library learned on one task distribution transfers to a held-out distribution. Measure whether library-equipped models show greater support-set expansion than library-free models.

**Kill gate:** Library learning produces reusable functions that are called by solver outputs on held-out tasks. Transfer is measurable: library-equipped models solve tasks that library-free models cannot.

**Compute:** 200-500 GPU-hours.

### Phase 6: Figures and Write-Up (Week 29-32)

**What:** Produce all figures, tables, and statistical analyses. Render the claims-gated notebook. Draft the paper.

**Kill gate:** All claims in the notebook are supported by the ledger data. Checker-B audit confirms no contamination or reward hacking in the reported results.

**Compute:** Laptop CPU for analysis and rendering.

### Phase 7: Public Notebook (Week 33-34)

**What:** Human review of all claims. Publish the gated notebook and paper preprint. Release code and data (excluding holdout answers).

**Kill gate:** At least one external reviewer reproduces the key result from the released code and data.

**Compute:** None.

## Compute Budget Summary

| Phase | Compute Type | Budget |
|-------|-------------|--------|
| 0 | Laptop CPU | Free |
| 1 | API credits | ~$50-200 |
| 2 | Single GPU | ~100 GPU-hours |
| 3 | Single GPU | ~200-500 GPU-hours |
| 4 | 1-4 GPUs | ~500-2000 GPU-hours |
| 5 | Single GPU | ~200-500 GPU-hours |
| 6-7 | Laptop CPU | Free |

**Total estimated GPU-hours:** 1000-3100. Feasible on a single RTX 4090 over 2-4 months, or on cloud instances over a few weeks.

## Hardware Notes

- **Development:** Any laptop with Python 3.10+. Tests and mock loop run CPU-only.
- **Training:** Consumer GPU with >=24 GB VRAM (RTX 3090/4090) for 1-3B parameter models with LoRA. Larger models (7-8B) may require 48 GB (A6000) or quantization (4-bit QLoRA).
- **Parallel arms:** Multiple arms can run concurrently on separate GPUs if available, since arms are independent.
- **Fallback:** If GPU is unavailable, Phase 2+ can use a cloud instance (Lambda Labs, RunPod, or similar) at ~$0.50-2.00/GPU-hour.
