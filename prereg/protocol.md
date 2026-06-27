# Pre-Registration Protocol

This file is a template for the frozen protocol that must be completed before
the full battery runs.

## Primary Question

Does any recursive/self-improvement arm produce per-problem support-set
expansion beyond the base high-k, STaR/ReST, matched-distillation,
random-reward, and format-only controls?

## Primary Endpoint

The primary endpoint is the number of held-out tasks classified as `gained`
relative to the base high-k support set and independently verified by checker B.

## Required Controls

- Base high-k sampling.
- Vanilla GRPO/RLVR.
- ProRL-style prolonged RL.
- Exploration-preserving RL.
- SvS/SPIRAL-style self-play.
- STaR/ReST SFT-on-verified-samples.
- Matched frontier-token distillation.
- Random reward.
- Format-only reward.
- No-frontier replay.
- Library disabled/frozen/shuffled/random-motif ablations.
- Checker-B audit.

## Stop Conditions

- The proposer cannot maintain tasks in the target success band.
- Checker A and checker B disagree above the pre-registered threshold.
- Holdout access occurs outside the frozen evaluation path.
- Control arms show support expansion comparable to treatment arms.

