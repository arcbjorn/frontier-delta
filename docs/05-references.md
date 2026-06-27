# 05 -- References

This bibliography lists the papers and projects that shape
Frontier Delta. Each entry gives the role the source plays in the
current design or in a deferred direction.

## Runtime Agents and Scaffolded Improvement

1. [ReAct](https://arxiv.org/abs/2210.03629) -- reasoning/action scaffold; useful as a runtime sharpening baseline, not as the central weight-update mechanism.
2. [Reflexion](https://arxiv.org/abs/2303.11366) -- verbal reinforcement and reflection; motivates a non-weight-update baseline.
3. [Generative Agents](https://arxiv.org/abs/2304.03442) -- memory/reflection architecture; informs why memory alone is not support-set expansion.
4. [Voyager](https://arxiv.org/abs/2305.16291) -- open-ended skill library agent; motivates later library-transfer studies.
5. [Darwin Godel Machine](https://arxiv.org/abs/2505.22954) -- self-modifying scaffold with evaluator feedback; deferred because v1 measures solver support-set movement.
6. [AlphaEvolve](https://arxiv.org/abs/2506.13131) -- evolutionary algorithm discovery; motivates evaluator-gated search but is not the v1 mechanism.
7. [AI Scientist-v2](https://arxiv.org/abs/2504.08066) -- automated research loop; rejected as a core mechanism because this project measures model capability movement, not research production.

## Self-Generated Data and Weight Updates

8. [STaR](https://arxiv.org/abs/2203.14465) -- self-generated reasoning data with filtering; motivates the SFT-on-verified-samples arm.
9. [ReST](https://arxiv.org/abs/2308.08998) -- reinforced self-training; motivates a filtered self-training baseline.
10. [SEAL](https://arxiv.org/abs/2506.10943) -- self-adapting language models; motivates later studies of update operators and forgetting.
11. [Algorithm Distillation](https://arxiv.org/abs/2210.14215) -- distills learning/search behavior into a policy; deferred until the loop has a real rollout engine.
12. [LoRA](https://arxiv.org/abs/2106.09685) -- low-rank adapter training; intended small-compute update mechanism.
13. [QLoRA](https://arxiv.org/abs/2305.14314) -- quantized adapter training; fallback for larger solvers on limited VRAM.
14. [DeepSeekMath / GRPO](https://arxiv.org/abs/2402.03300) -- source for GRPO-style policy optimization used in later training phases.

## RLVR, Self-Play, and Exploration

15. [Absolute Zero Reasoner](https://arxiv.org/abs/2505.03335) -- self-play reasoning without curated external data; informs proposer-solver loops.
16. [SPIRAL](https://arxiv.org/abs/2506.24119) -- self-play reasoning transfer; motivates the self-play arm.
17. [R-Zero](https://arxiv.org/abs/2508.05004) -- self-evolving reasoning; motivates proposer viability and label-decay checks.
18. [SvS](https://arxiv.org/abs/2508.14029) -- diversity-preserving self-play; motivates expansion-oriented self-play controls.
19. [TTRL](https://arxiv.org/abs/2504.16084) -- test-time reinforcement learning; deferred as an inference-time extension.
20. [ProRL](https://arxiv.org/abs/2505.24864) -- prolonged RL for reasoning; motivates an explicit prolonged-RL arm.
21. [Pass@k Training](https://arxiv.org/abs/2508.10751) -- trains for high-k success; motivates exploration-preserving reward design.
22. [SAGE](https://arxiv.org/abs/2605.18864) -- guided exploration for RLVR; motivates diversity pressure in the treatment arm.
23. [Bayesian Boundary Gating / Diversity Collapse](https://arxiv.org/abs/2606.15455) -- motivates boundary-aware exploration and entropy/AST-diversity metrics.
24. [Transfer-Aware Curriculum](https://arxiv.org/abs/2606.25178) -- motivates curriculum evaluation that distinguishes in-domain gains from transfer.

## Limits, Verification, and Measurement

25. [LLMs Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) -- supports using external verifiers instead of self-critique as reward.
26. [Mind the Gap / generation-verification gap](https://arxiv.org/abs/2412.02674) -- motivates separating generation from checking.
27. [On the Limits of Self-Improving LLMs](https://arxiv.org/abs/2601.05280) -- frames why recursive loops can stall without grounded signal.
28. [Self-Improvement Sharpening](https://arxiv.org/abs/2412.01951) -- motivates the sharpening-versus-expansion null hypothesis.
29. [Spurious Rewards](https://arxiv.org/abs/2506.10947) -- motivates random-reward and format-only controls.
30. [Codex / pass@k estimator](https://arxiv.org/abs/2107.03374) -- source for the unbiased pass@k estimator in `src/frontier_delta/passk.py`.
31. [ARC-AGI / On the Measure of Intelligence](https://arxiv.org/abs/1911.01547) -- motivates abstraction-focused, guess-resistant held-out evaluation.
32. [Cognitive Behaviors](https://arxiv.org/abs/2503.01307) -- motivates later analysis of verification, backtracking, and subgoaling behavior.

## Program Synthesis, Libraries, and Abstraction

33. [DreamCoder](https://arxiv.org/abs/2006.08381) -- wake-sleep library learning; motivates Phase 5 library transfer.
34. [LILO](https://arxiv.org/abs/2310.19791) -- language-informed library induction; motivates language-assisted abstraction discovery.
35. [Stitch](https://arxiv.org/abs/2211.16605) -- program compression and library learning; motivates motif/library consolidation.
36. [Hindsight Experience Replay](https://arxiv.org/abs/1707.01495) -- considered and rejected for v1 because fixed program specs do not naturally support goal relabeling.
37. [Reasoning Gym](https://arxiv.org/abs/2505.24760) -- procedural reasoning environments; possible later task source.
38. [GURU](https://arxiv.org/abs/2506.14965) -- multi-domain reasoning transfer; informs later transfer-distance ladders.

## Open-Endedness, Worlds, and Deferred Generality

39. [POET](https://arxiv.org/abs/1901.01753) -- open-ended environment generation; deferred because v1 requires deterministic verification.
40. [OMNI](https://arxiv.org/abs/2306.01711) -- foundation-model-guided interestingness for open-ended tasks; deferred as a future curriculum direction.
41. [World Models](https://arxiv.org/abs/1803.10122) -- latent environment modeling; deferred because simulator fidelity is out of scope.
42. [DreamerV3](https://arxiv.org/abs/2301.04104) -- general world-model RL; informs deferred world-model loops.
43. [Genie](https://arxiv.org/abs/2402.15391) -- generative interactive environments; deferred because task execution is harder to verify.
44. [SIMA](https://deepmind.google/discover/blog/sima-generalist-ai-agent-for-3d-virtual-environments/) -- generalist instructed agent project; deferred because embodied task verification is beyond v1.

## Infrastructure and Reporting

45. [PEFT](https://github.com/huggingface/peft) -- practical adapter-training implementation candidate.
46. [TRL](https://github.com/huggingface/trl) -- practical RL fine-tuning implementation candidate.
47. [vLLM](https://github.com/vllm-project/vllm) -- rollout backend candidate for later batched solver sampling.
48. [nsjail](https://github.com/google/nsjail) -- candidate production sandbox for untrusted generated code.
49. [E2B](https://github.com/e2b-dev/E2B) -- candidate managed sandbox for untrusted generated code.
