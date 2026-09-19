# Codex Advisor

Codex Advisor is a model-agnostic orchestration plugin for Codex. The active parent
model owns the task, architecture, integration, verification, and final answer. It
delegates only bounded work that benefits from another context, choosing among the
models and reasoning efforts exposed by the current Codex host.

This fork intentionally does not use GPT-6 Astra. `gpt-5.6-sol` is the recommended
parent for demanding work. Lower-cost models can handle well-bounded work without
making them the acceptance authority.

## Install

~~~sh
codex plugin marketplace add jmrichardson/codex-advisor --ref main
codex plugin add codex-advisor@codex-advisor
~~~

If Astra Advisor is already installed, install and validate Codex Advisor first,
then remove the old plugin and marketplace:

~~~sh
codex plugin remove astra-advisor@astra-advisor
codex plugin marketplace remove astra-advisor
~~~

Start a fresh task after installation. You can invoke the skill explicitly with:

~~~text
Use $codex-advisor:orchestration to plan, route, implement, verify, and review this work.
~~~

The plugin also opts into implicit invocation. To make it the normal workflow for
new local tasks, add this rule to `~/.codex/AGENTS.md`:

~~~md
For substantial multi-step tasks, use the installed `codex-advisor:orchestration`
skill. Skip it for simple answers, status checks, formatting, and trivial edits.
~~~

Codex loads global instructions when a task starts, so an already-running task may
need to be restarted. Implicit skill selection is best-effort; the global instruction
is the durable default.

Recommended global defaults in `~/.codex/config.toml` are:

~~~toml
model = "gpt-5.6-sol"
model_reasoning_effort = "high"

[agents]
enabled = true
default_subagent_model = "gpt-5.6-terra"
default_subagent_reasoning_effort = "medium"
~~~

The parent model and effort are not changed by the skill. Select a different parent
when starting a task if desired.

## Routing policy

Codex Advisor starts with a capability preflight and records the parent model and
effort as observed or unobservable. It skips delegation when the task is trivial or
when sharing context would cost more than it saves.

When delegation helps, the parent uses native Codex subagents and selects from the
live tool schema. The current routing guidance is:

| Work shape | Typical model |
| --- | --- |
| Narrow, mechanical, repetitive, easy to verify | `gpt-5.6-luna` |
| Exploration, documentation, bounded implementation | `gpt-5.6-terra` |
| Architecture, difficult debugging, security, high-risk review | `gpt-5.6-sol` |

These are heuristics, not fixed roles. Live model availability and supported efforts
win. Every delegation has one bounded deliverable, explicit ownership, and a stated
model-selection reason. Concurrent writers must own disjoint files or surfaces.

For substantial or high-risk implementation, the parent inspects the complete diff,
runs the relevant checks, and obtains a fresh read-only review, normally from Sol.
The parent remains responsible for evaluating findings and accepting the result.

Codex Advisor reports a concise route-and-verification receipt. It does not estimate
API-equivalent costs from incomplete native telemetry or claim that one model's token
workload predicts another model's total cost.

## Boundaries

- Separate Codex app tasks are created only when the user explicitly requests them.
- ChatGPT Work cloud task creation may not expose model or reasoning controls.
- The plugin never uses API keys, nested Codex CLIs, or fabricated tools to bypass a
  host limitation.
- User instructions, repository instructions, and live tool schemas override the
  routing heuristics.

## Development

~~~sh
python -m pip install -r requirements-dev.txt
python plugins/codex-advisor/scripts/verify.py
python -m unittest discover -s plugins/codex-advisor/tests -p "test_*.py"
~~~

For local installation, use the absolute checkout path as the marketplace source and
then add `codex-advisor@codex-advisor`.

This project is a model-agnostic fork of
[DannyMac180/astra-advisor](https://github.com/DannyMac180/astra-advisor), retained
under its MIT license. The original copyright notice remains in [LICENSE](LICENSE).

For operational detail, see the
[orchestration reference](plugins/codex-advisor/skills/orchestration/references/operations.md).
