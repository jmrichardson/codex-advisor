---
name: orchestration
description: "Plan, route, implement, verify, and review substantial multi-step work with the active Codex parent and dynamically selected native subagents. Use for complex builds, migrations, broad refactors, investigations, or high-risk changes; skip simple answers and trivial edits."
---

# Codex Advisor Orchestration

Act as the architect and acceptance owner. The active parent model owns intent,
architecture, decomposition, integration, verification, and the final answer. This
skill does not change the parent model or reasoning effort. Record those settings as
observed when runtime metadata exposes them; otherwise say `unobservable`.

This skill is model-agnostic, but never route work to GPT-6 Astra. Sol is the
recommended parent and the default choice for difficult or high-risk delegated work.
If a weaker parent is selected, keep it in charge but use Sol for architecture or
review when the task's risk warrants it and native delegation is available.

Before implementation or delegation, emit a short user-visible declaration:

~~~text
CODEX ADVISOR ROUTE
parent: <observed model or unobservable> / <observed effort or unobservable>
delegation: <none, or each selected model and effort>
risk: <concise task-specific rationale>
~~~

Read [the operations reference](references/operations.md) before the first
delegation. Skip delegation for trivial work, tightly coupled work that cannot be
split safely, or work whose context-transfer cost exceeds its benefit.

Use native `collaboration.spawn_agent` only when exposed by the current tool schema.
Give each subagent a concrete, bounded, independent deliverable. Set an explicit
supported model, reasoning effort, and `fork_turns: none`. Use live tool metadata as
the authority. Never silently substitute a model, effort, role, or fabricated tool.

Select dynamically from available non-Astra models. Current guidance:

- Luna: narrow, mechanical, repetitive work with objective checks.
- Terra: exploration, documentation, and bounded implementation.
- Sol: architecture, difficult debugging, security-sensitive work, high-risk changes,
  and fresh review.

These are heuristics, not fixed roles. Prefer the least expensive model that can
reliably produce the deliverable, then raise effort or model strength with risk and
ambiguity. One writer owns each file or surface. Parallel writers must have disjoint
ownership. Preserve user and concurrent-agent changes.

The parent continues useful independent work while subagents run, integrates their
results, inspects changed files, and reruns relevant checks. A subagent's claim is
evidence to inspect, not acceptance.

For substantial or high-risk implementation, obtain a fresh read-only review after
parent verification. Normally select Sol at a live-supported high effort. Give the
reviewer the actual diff, constraints, and verification evidence, and require:

~~~text
CODEX ADVISOR REVIEW
VERDICT: ship | fix-first | rethink
REASON: <evidence-based reason>
FINDINGS: <precise findings or none>
RESIDUAL RISK: <remaining risk or none>
~~~

The reviewer never fixes its own findings. On `fix-first`, the parent evaluates and
applies justified fixes, verifies again, and obtains a fresh review when the change
remains substantial or high-risk. On `rethink`, revise the approach before claiming
completion. If native review is unavailable, disclose that limitation and do not
claim independent review.

Separate Codex app tasks require an explicit user request. Do not create them as a
delegation workaround. ChatGPT Work cloud tasks may omit model and reasoning controls;
do not promise a pin that the public schema cannot enforce. Never use API keys, nested
Codex CLIs, or invented tools to bypass a host limitation.

## Lifecycle and completion receipt

Before every delegation, show its name, bounded deliverable, ownership, requested
model and effort, and selection reason. On return, show actual status and any
runtime-observed model or effort. Requested settings are not proof of realized
settings; use `unobservable` when metadata is absent. Report meaningful changes
without polling narration.

End every routed task with a concise receipt:

~~~text
CODEX ADVISOR RESULT
parent: <observed model/effort or unobservable>
delegation: <none, or requested and observed delegates with outcomes>
verification: <checks run and results>
review: <verdict and reviewer, not required, or unavailable>
limits: <material telemetry or capability limits, or none>
~~~

Do not estimate API cost from missing native telemetry, infer token counts from text
length, or claim counterfactual savings. It is enough to explain why each routed model
was appropriate and what evidence supports acceptance.
