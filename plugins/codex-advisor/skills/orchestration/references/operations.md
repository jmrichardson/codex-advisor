# Codex Advisor operations

This reference contains the detailed routing and evidence rules. Live tool schemas,
user instructions, and repository instructions take precedence.

## Decide whether to route

Use the parent alone when the task is small, the work is tightly coupled, another
context would duplicate effort, or verification is cheaper than delegation. Route
only a deliverable that can be stated with clear inputs, ownership, and acceptance
evidence.

Useful independent shapes include repository reconnaissance, external research,
implementation in disjoint files, focused test work, and read-only review. Do not
delegate the final integration or acceptance decision.

## Select a model and effort

Inspect the models and efforts in the current `collaboration.spawn_agent` schema.
The live schema wins over this snapshot:

| Model | Current routing preference |
| --- | --- |
| `gpt-5.6-luna` | Mechanical or repetitive work with strong checks |
| `gpt-5.6-terra` | Exploration, documentation, bounded implementation |
| `gpt-5.6-sol` | Architecture, hard debugging, high-risk work, review |

Never select `gpt-6-astra`. Start with the least expensive model that can reliably
complete the bounded deliverable. Increase effort for ambiguity, large search spaces,
or consequential failure. Increase model strength when synthesis, architecture,
security, or subtle correctness dominates. Do not encode permanent role-to-model
mappings; select from the actual task.

Pass the selected controls explicitly:

~~~text
model: <available non-Astra model>
reasoning_effort: <supported effort>
fork_turns: none
~~~

If a selected control is unavailable or conflicts with higher-priority instructions,
do not silently substitute it. Re-plan with the parent or report the limitation.

## Assign and integrate

Each message must state:

- the single bounded outcome;
- owned files or read-only scope;
- constraints and relevant repository rules;
- required evidence and return format;
- that the agent is not alone and must preserve unrelated edits when writing.

Only parallelize truly independent work. Assign one writer per file or surface and
avoid asking parent and child to make the same change. The parent tracks agent IDs,
waits without noisy polling, evaluates returned evidence, integrates compatible
results, and verifies the combined state.

Use these user-visible lifecycle forms:

~~~text
CODEX ADVISOR DELEGATE <name>
task: <bounded deliverable and ownership>
requested: <model> / <effort>
reason: <task-specific selection reason>

CODEX ADVISOR DELEGATE RESULT <name> / <agent ID or unavailable>
status: <completed, failed, interrupted, or blocked>
requested: <model> / <effort>
observed: <model or unobservable> / <effort or unobservable>
evidence: <returned checks or limitation>
~~~

## Verify and review

The parent inspects the complete accumulated diff and reruns relevant checks. Match
verification to the risk: focused checks for isolated changes, broader suites for
cross-cutting behavior, and explicit evidence for security or data mutations.

For substantial or high-risk implementation, start a fresh read-only reviewer after
verification. Sol at high or greater effort is the normal choice when supported, but
live availability and task risk remain authoritative. Provide the actual diff,
requirements, repository rules, and check output. Require the structured verdict in
the main skill. A reviewer is independent only when it has not implemented the same
change.

The parent evaluates findings against the code. Apply justified findings, rerun
checks, and seek a fresh review when appropriate. State unresolved material risks or
review unavailability plainly.

## App and cloud boundaries

Native collaboration subagents are internal work for the current task. Separate app
tasks are user-visible and require an explicit request. For explicit project-task
creation, first inspect saved projects and follow the host's project/worktree rules.

Some cloud task APIs do not expose arbitrary model or reasoning controls. Omit fields
the schema does not accept and never claim an unenforced selection. Do not use API
keys, a nested CLI, or an external inference service as a workaround.

## Completion evidence

Report selected and observed settings separately. Summarize delegated outcomes,
parent verification, independent review, and material limitations. Native telemetry
may not expose billing-grade token usage; unknown is not zero. Do not manufacture a
cost receipt or a same-token counterfactual from incomplete data.
