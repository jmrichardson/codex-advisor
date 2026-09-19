from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by a missing dev dependency
    raise SystemExit("PyYAML is required; install requirements-dev.txt") from exc


PLUGIN_NAME = "codex-advisor"
VERSION = "0.3.0"
REPOSITORY = "https://github.com/jmrichardson/codex-advisor"


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)", text)


def main() -> int:
    script = Path(__file__).resolve()
    plugin = script.parent.parent
    repo = plugin.parent.parent
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    def load_json(path: Path, label: str) -> dict:
        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"missing {label}: {path}")
            return {}
        except OSError as exc:
            errors.append(f"cannot read {label}: {exc}")
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {label}: {exc}")
            return {}
        require(isinstance(value, dict), f"{label} must be a JSON object")
        return value if isinstance(value, dict) else {}

    def check_links(path: Path, text: str) -> None:
        for raw_target in markdown_links(text):
            parsed = urlsplit(raw_target)
            if parsed.scheme or parsed.netloc or raw_target.startswith("#"):
                continue
            target = (path.parent / parsed.path).resolve()
            require(target.is_relative_to(repo), f"link escapes repository in {path}: {raw_target}")
            require(target.is_file(), f"missing linked file in {path}: {raw_target}")

    manifest = load_json(plugin / ".codex-plugin" / "plugin.json", "plugin manifest")
    require(manifest.get("name") == PLUGIN_NAME, "manifest name must be codex-advisor")
    require(manifest.get("version") == VERSION, f"manifest version must be {VERSION}")
    require(manifest.get("repository") == REPOSITORY, "manifest repository must point to the fork")
    require(manifest.get("homepage") == f"{REPOSITORY}#readme", "manifest homepage must point to the fork")
    require(manifest.get("license") == "MIT", "manifest license must be MIT")
    require(manifest.get("skills") == "./skills/", "manifest skills path must be ./skills/")

    interface = manifest.get("interface")
    require(isinstance(interface, dict), "manifest interface must be an object")
    if isinstance(interface, dict):
        require(interface.get("displayName") == "Codex Advisor", "display name must be Codex Advisor")
        prompts = interface.get("defaultPrompt")
        require(isinstance(prompts, list), "defaultPrompt must be an array")
        if isinstance(prompts, list):
            require(
                any("$codex-advisor:orchestration" in item for item in prompts if isinstance(item, str)),
                "defaultPrompt must invoke $codex-advisor:orchestration",
            )

    marketplace = load_json(repo / ".agents" / "plugins" / "marketplace.json", "marketplace")
    require(marketplace.get("name") == PLUGIN_NAME, "marketplace name must be codex-advisor")
    entries = marketplace.get("plugins")
    require(isinstance(entries, list) and len(entries) == 1, "marketplace must contain one plugin")
    entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else None
    require(isinstance(entry, dict), "marketplace plugin entry must be an object")
    if isinstance(entry, dict):
        require(entry.get("name") == PLUGIN_NAME, "marketplace plugin name must be codex-advisor")
        source = entry.get("source")
        require(isinstance(source, dict), "marketplace source must be an object")
        if isinstance(source, dict):
            require(source.get("path") == "./plugins/codex-advisor", "marketplace source path is incorrect")

    skill = plugin / "skills" / "orchestration" / "SKILL.md"
    operations = skill.parent / "references" / "operations.md"
    ui = skill.parent / "agents" / "openai.yaml"
    readme = repo / "README.md"
    workflow = repo / ".github" / "workflows" / "verify.yml"
    license_path = repo / "LICENSE"
    for path, label in (
        (skill, "skill"),
        (operations, "operations reference"),
        (ui, "skill UI metadata"),
        (readme, "README"),
        (workflow, "CI workflow"),
        (license_path, "license"),
    ):
        require(path.is_file(), f"missing {label}: {path}")

    skill_text = skill.read_text(encoding="utf-8") if skill.is_file() else ""
    operations_text = operations.read_text(encoding="utf-8") if operations.is_file() else ""
    readme_text = readme.read_text(encoding="utf-8") if readme.is_file() else ""

    if skill_text:
        normalized_skill = " ".join(skill_text.split())
        require(skill_text.startswith("---\n"), "skill must start with YAML frontmatter")
        require("name: orchestration" in skill_text[:500], "skill name must be orchestration")
        for phrase in (
            "Skip delegation for trivial work",
            "Use live tool metadata as the authority",
            "One writer owns each file or surface",
            "fresh read-only review",
            "CODEX ADVISOR RESULT",
            "never route work to GPT-6 Astra",
        ):
            require(phrase in normalized_skill, f"skill is missing policy: {phrase}")
        require("API-EQUIVALENT COST RECEIPT" not in skill_text, "legacy cost receipt remains in skill")

    if operations_text:
        for model in ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"):
            require(model in operations_text, f"operations reference is missing {model}")
        require("Never select `gpt-6-astra`" in operations_text, "operations must exclude Astra routing")

    if ui.is_file():
        ui_text = ui.read_text(encoding="utf-8")
        try:
            ui_data = yaml.safe_load(ui_text)
        except yaml.YAMLError as exc:
            errors.append(f"invalid YAML in skill UI metadata: {exc}")
            ui_data = {}
        require(isinstance(ui_data, dict), "skill UI metadata must be a YAML object")
        if isinstance(ui_data, dict):
            ui_interface = ui_data.get("interface")
            ui_policy = ui_data.get("policy")
            require(isinstance(ui_interface, dict), "skill UI interface must be an object")
            require(isinstance(ui_policy, dict), "skill UI policy must be an object")
            if isinstance(ui_interface, dict):
                require(
                    "$codex-advisor:orchestration" in str(ui_interface.get("default_prompt", "")),
                    "UI prompt must invoke Codex Advisor",
                )
            if isinstance(ui_policy, dict):
                require(ui_policy.get("allow_implicit_invocation") is True, "implicit invocation must be enabled")

    if readme_text:
        require("$codex-advisor:orchestration" in readme_text, "README must show explicit invocation")
        require("~/.codex/AGENTS.md" in readme_text, "README must document durable default setup")
        require("DannyMac180/astra-advisor" in readme_text, "README must retain upstream attribution")

    if workflow.is_file():
        workflow_text = workflow.read_text(encoding="utf-8")
        require("plugins/codex-advisor/scripts/verify.py" in workflow_text, "CI must run the verifier")

    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        require("Copyright (c) 2026 Daniel McAteer" in license_text, "MIT attribution must be retained")

    for path, text in (
        (readme, readme_text),
        (skill, skill_text),
        (operations, operations_text),
    ):
        check_links(path, text)

    legacy_artifacts = (
        plugin / "scripts" / "cost_receipt.py",
        plugin / "pricing",
        plugin / "examples" / "illustrative-usage.json",
        plugin / "tests" / "test_cost_receipt.py",
    )
    for path in legacy_artifacts:
        require(not path.exists(), f"legacy cost artifact remains: {path.relative_to(repo)}")

    require(
        (plugin / "tests" / "test_verifier.py").is_file(),
        "missing verifier regression tests",
    )

    for path in plugin.rglob("*.toml"):
        errors.append(f"static role TOML is not allowed: {path.relative_to(plugin)}")

    if errors:
        print("VERIFY FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VERIFY PASSED")
    print("manifest, marketplace, routing policy, references, attribution, and CI are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
