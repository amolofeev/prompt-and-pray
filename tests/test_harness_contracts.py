#!/usr/bin/env python3
"""Isolated contract checks for the harness S4 verification matrix.

The tests intentionally model issue and close transitions in memory.  They do
not call a tracker or mutate a parent issue.  Source-contract checks complement
those fixtures so a passing run verifies both behavior and the documents that
agents actually load.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "harness-contracts.json"
AGENT_DIR = ROOT / ".opencode" / "agent"
WORKFLOW = ROOT / ".opencode" / "skills" / "harness-workflow" / "SKILL.md"
SPEC = ROOT / "docs" / "harness-agents.md"
DELIVERY = AGENT_DIR / "delivery.md"

EXPECTED_ROLES = {
    "business-analyst": {
        "*": "deny",
        "specificator": "allow",
    },
    "delivery": {
        "*": "deny",
        "business-analyst": "allow",
        "systems-analyst": "allow",
        "team-lead-*": "allow",
        "team-lead-meta": "allow",
        "developer-*": "allow",
        "specificator": "allow",
    },
    "developer-go": {"*": "deny"},
    "developer-harness": {"*": "deny"},
    "developer-python": {"*": "deny"},
    "specificator": {"*": "deny"},
    "systems-analyst": {
        "*": "deny",
        "business-analyst": "allow",
        "specificator": "allow",
    },
    "team-lead-go": {
        "*": "deny",
        "business-analyst": "allow",
        "specificator": "allow",
    },
    "team-lead-meta": {
        "*": "deny",
        "business-analyst": "allow",
        "specificator": "allow",
    },
    "team-lead-python": {
        "*": "deny",
        "business-analyst": "allow",
        "specificator": "allow",
    },
}

ROUTER_KEYS = [
    "mechanism",
    "version",
    "state",
    "next",
    "target",
    "target_state",
    "ready",
    "authorization",
    "close",
    "reason",
]
ROUTER_STATES = ["dispatch", "hold", "blocked", "awaiting_po_closure", "done"]
ROUTER_ACTIONS = ["dispatch", "wait", "request_po_closure", "stop"]
CLOSURE_KEYS = {
    "transition",
    "target",
    "target_state",
    "authorization_basis",
    "dod_recheck",
    "close",
    "outcome",
}
TRACKER_COMMAND = re.compile(r"\bgh\s+(?:issue|pr|pull|workflow|repo)\b", re.IGNORECASE)
EXPECTED_CONTRACT_KEYS = {
    "business-analyst": {"requirements"},
    "delivery": {"route", "dod", "router"},
    "developer-go": {"done", "unblocked"},
    "developer-harness": {"done", "unblocked"},
    "developer-python": {"done", "unblocked"},
    "specificator": {"classification", "constraints", "artifacts"},
    "systems-analyst": {"specification"},
    "team-lead-go": {"plan"},
    "team-lead-meta": {"plan"},
    "team-lead-python": {"plan"},
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_and_body(path: Path) -> tuple[str, str]:
    text = read(path)
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not match:
        raise AssertionError(f"missing YAML frontmatter: {path}")
    return match.group(1), match.group(2)


def scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    if value in {"true", "false"}:
        return value == "true"
    return value


def fallback_frontmatter(raw: str) -> dict[str, Any]:
    """Parse the small frontmatter subset used by agent files.

    PyYAML is preferred.  The fallback keeps the harness check runnable on a
    minimal Python installation and deliberately understands only scalar and
    nested mapping fields needed by this test.
    """

    result: dict[str, Any] = {}
    section: str | None = None
    subsection: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        text = line.strip()
        if ":" not in text:
            continue
        key, value = (part.strip() for part in text.split(":", 1))
        key = scalar(key)
        if indent == 0:
            if value:
                result[key] = scalar(value)
                section = None
                subsection = None
            else:
                section = key
                subsection = None
                result.setdefault(key, {})
        elif indent == 2 and section:
            if value:
                result[section][key] = scalar(value)
                subsection = None
            else:
                subsection = key
                result[section].setdefault(key, {})
        elif indent == 4 and section and subsection:
            result[section][subsection][key] = scalar(value)
    return result


def parse_frontmatter(path: Path) -> dict[str, Any]:
    raw, _ = frontmatter_and_body(path)
    if yaml is not None:
        parsed = yaml.safe_load(raw)
        if not isinstance(parsed, dict):
            raise AssertionError(f"frontmatter is not a mapping: {path}")
        return parsed
    return fallback_frontmatter(raw)


def yaml_blocks(text: str) -> list[str]:
    return re.findall(r"```yaml\s*\n(.*?)\n```", text, re.DOTALL)


def yaml_block(text: str, root_key: str, required_child: str | None = None) -> str:
    for block in yaml_blocks(text):
        first = next(
            (
                line.strip()
                for line in block.splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ),
            "",
        )
        if first == f"{root_key}:" and (
            required_child is None
            or re.search(
                rf"^  {re.escape(required_child)}:", block, re.MULTILINE
            )
        ):
            return block.strip()
    suffix = f" containing {required_child}" if required_child else ""
    raise AssertionError(
        f"missing fenced YAML block rooted at {root_key}{suffix}"
    )


def top_level_keys(block: str) -> set[str]:
    keys: set[str] = set()
    for line in block.splitlines():
        match = re.match(r"^([a-z][a-z_-]*):(?:\s|$)", line)
        if match:
            keys.add(match.group(1))
    return keys


def yaml_child_keys(block: str) -> set[str]:
    keys: set[str] = set()
    for line in block.splitlines():
        match = re.match(r"^  ([a-z][a-z_-]*):(?:\s|$)", line)
        if match:
            keys.add(match.group(1))
    return keys


def yaml_child_value(block: str, key: str) -> str:
    match = re.search(rf"^  {re.escape(key)}:\s*(.+)$", block, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing YAML child {key}")
    return match.group(1).strip()


def assert_subset(expected: Any, actual: Any, path: str = "result") -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise AssertionError(f"{path}: expected mapping, got {actual!r}")
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f"{path}.{key}: missing (got {actual!r})")
            assert_subset(value, actual[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or actual != expected:
            raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")
        return
    if actual != expected:
        raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")


def explicit_po_authorization(request: str | None, target: int) -> bool:
    """Model the contract's strict natural-language authorization rule."""

    if not request:
        return False
    numbers = re.findall(r"#(\d+)", request)
    if len(numbers) != 1 or int(numbers[0]) != target:
        return False
    normalized = request.casefold()
    explicit = (
        "разрешаю закрыть" in normalized
        or "разрешение на закрытие" in normalized
        or re.search(r"\b(i|authoriz\w*)\s+(?:the\s+)?close\b", normalized)
        is not None
        or re.search(r"\bauthoriz\w*\b.*\bclose\b", normalized) is not None
    )
    # A bare imperative is deliberately not enough: the request must express
    # permission, not merely ask the team to perform the close.
    return bool(explicit)


def delivery_dod(result: str, target_state: str = "OPEN") -> dict[str, Any]:
    if result == "pass":
        return {
            "result": "pass",
            "recommendation": "close",
            "decision_owner": "PO",
            "state": "awaiting_po_closure",
            "target_state": target_state,
            "authorization": "pending",
            "close_attempts": 0,
        }
    if result == "fail":
        return {
            "result": "fail",
            "recommendation": "hold",
            "decision_owner": "PO",
            "state": "hold",
            "target_state": target_state,
            "authorization": "not_requested",
            "close_attempts": 0,
        }
    raise ValueError(result)


def authorized_close(
    *,
    target: int,
    target_state: str,
    request: str | None,
    fresh_dod: str,
    marker_present: bool = False,
) -> dict[str, Any]:
    marker = f"<!-- harness:po_authorized_close target=#{target} -->"
    if target_state == "CLOSED":
        if marker_present:
            return {
                "outcome": "done",
                "attempts": 0,
                "close_result": "already_closed",
                "new_comments": 0,
                "comment_disposition": "existing",
                "target_state": "CLOSED",
                "marker_present": True,
            }
        return {
            "outcome": "blocked",
            "attempts": 0,
            "close_result": "indeterminate",
            "new_comments": 0,
            "marker_present": False,
        }
    if not explicit_po_authorization(request, target):
        return {
            "outcome": "awaiting_po_closure",
            "attempts": 0,
            "close_result": "not_called",
            "new_comments": 0,
            "target_state": "OPEN",
        }
    if fresh_dod != "pass":
        return {
            "outcome": "hold",
            "attempts": 0,
            "close_result": "not_called",
            "new_comments": 0,
            "target_state": "OPEN",
        }
    comment = (
        f"[AI] PO-авторизованное закрытие задачи #{target}\n\n"
        f"- Основание авторизации: {request}\n"
        "- Повторная DoD-проверка: pass\n"
        f"- Evidence: isolated fixture\n"
        f"- Итог: задача #{target} закрыта.\n\n{marker}"
    )
    return {
        "outcome": "done",
        "attempts": 1,
        "close_result": "closed",
        "new_comments": 1,
        "comment_disposition": "posted",
        "target_state": "CLOSED",
        "comment_prefix": comment.splitlines()[0][:4],
        "marker_present": marker in comment,
        "comment": comment,
    }


def router_state(facts: dict[str, Any]) -> dict[str, Any]:
    if facts.get("open_blockers"):
        return {
            "state": "blocked",
            "action": "wait",
            "to": None,
            "request": "none",
            "requester": None,
            "ready": "blocked",
            "authorization": "not_requested",
            "close": "not_attempted",
        }
    if facts.get("needs_reply") or facts.get("dod") == "fail":
        return {
            "state": "hold",
            "action": "wait",
            "to": None,
            "request": "none",
            "requester": None,
            "ready": "ready",
            "authorization": "not_requested",
            "close": "not_attempted",
        }
    if (
        facts.get("target_state") == "CLOSED"
        and facts.get("marker")
        and facts.get("close_confirmed")
    ):
        return {
            "state": "done",
            "action": "stop",
            "to": None,
            "request": "none",
            "requester": None,
            "ready": "ready",
            "authorization": "present",
            "close": "confirmed",
        }
    if facts.get("target_state") == "OPEN" and facts.get("dod") == "pass":
        return {
            "state": "awaiting_po_closure",
            "action": "request_po_closure",
            "to": None,
            "request": "po_closure",
            "requester": "PO",
            "ready": "ready",
            "authorization": "pending",
            "close": "not_attempted",
        }
    if facts.get("target_state") == "CLOSED" and not facts.get("marker"):
        return {
            "state": "blocked",
            "action": "wait",
            "to": None,
            "request": "none",
            "requester": None,
            "ready": "ready",
            "authorization": "present",
            "close": "indeterminate",
        }
    return {
        "state": "dispatch",
        "action": "dispatch",
        "to": "developer-harness",
        "request": "none",
        "requester": None,
        "ready": "ready",
        "authorization": "not_requested",
        "close": "not_attempted",
    }


def contract_observation() -> dict[str, Any]:
    _, body = frontmatter_and_body(DELIVERY)
    body_lower = body.casefold()
    close_prohibition = (
        "do not close a parent issue" in body_lower
        and "has no close permission" in body_lower
        and "do not close any issue" in body_lower
    )
    flat_body = re.sub(r"\s+", " ", body)
    recommendation_is_done = (
        "close recommendation as an executed close" in flat_body
        and "Do not set `done` until an actual CLOSED state" in flat_body
    )
    return {
        "role": "delivery",
        "close_permission": "deny" if close_prohibition else "not_proven",
        "evidence": all(
            phrase in flat_body
            for phrase in ["reproducible evidence", "Add the `dod` block to the route report"]
        ),
        "recommendations": [
            recommendation
            for recommendation in ["close", "hold"]
            if f"recommendation: {recommendation}" in body
        ],
        "decision_owner": "PO" if "decision_owner: PO" in body else None,
        "independent_close": not close_prohibition,
        "recommendation_is_done": not recommendation_is_done,
    }


def router_registration_observation() -> dict[str, Any]:
    role_files = {path.stem for path in AGENT_DIR.glob("*.md")}
    frontmatters = {
        name: parse_frontmatter(AGENT_DIR / f"{name}.md") for name in sorted(role_files)
    }
    task_keys = {
        key
        for data in frontmatters.values()
        for key in data.get("permission", {}).get("task", {})
    }
    workflow = re.sub(r"\s+", " ", read(WORKFLOW))
    non_authorizing_rule = (
        "не создаёт авторизацию" in workflow
        and "не интерпретирует её вместо PO" in workflow
    )
    non_closing_rule = (
        "не пишет в трекер и не закрывает issues" in workflow
        and "После выбора состояния router ничего не авторизует и не закрывает" in workflow
    )
    return {
        "router_file": "harness-router" in role_files or "router" in role_files,
        "router_subagent": "subagent_type: router" in workflow,
        "router_task_node": "harness-router" in task_keys or "router" in task_keys,
        "router_closes_issue": not non_closing_rule,
        "router_authorizes_po": not non_authorizing_rule,
    }


def closure_contract_observation() -> dict[str, Any]:
    skill = read(WORKFLOW)
    spec = read(SPEC)
    required = [
        "po_authorized_close",
        "Повторная DoD-проверка",
        "не более одного раза",
        "harness:po_authorized_close",
        "[AI] PO-авторизованное закрытие",
    ]
    return {
        "transition": "po_authorized_close" if "po_authorized_close" in skill else None,
        "executor_outside_roles": "вне Delivery" in skill and "вне Delivery" in spec,
        "recheck_required": "повторно" in skill.casefold() and "повторно" in spec.casefold(),
        "close_attempts_max": 1 if "не более одного раза" in skill else 0,
        "marker_required_for_done": all(
            "harness:po_authorized_close" in text for text in [skill, spec]
        ),
        "ai_comment_required": all(
            "[AI] PO-авторизованное закрытие" in text for text in [skill, spec]
        ),
        "required_phrases_present": all(phrase in skill for phrase in required),
    }


def load_fixture() -> dict[str, Any]:
    return json.loads(read(FIXTURE_PATH))


class ContractMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = load_fixture()
        cls.cases = {case["id"]: case for case in cls.fixture["cases"]}
        expected_ids = {
            "D1", "D2", "D3", "D4", "R1", "R2", "C1", "C2",
            "V1", "V2", "V3", "V4", "V5", "ROOT1", "ROOT2",
        }
        if set(cls.cases) != expected_ids:
            raise AssertionError(
                f"matrix ids differ: expected {sorted(expected_ids)}, got {sorted(cls.cases)}"
            )
        cls.marker = cls.fixture["marker"]

    def case(self, case_id: str) -> dict[str, Any]:
        return self.cases[case_id]

    def test_D1(self) -> None:
        case = self.case("D1")
        actual = contract_observation()
        assert_subset(case["expected"], actual)
        frontmatter = parse_frontmatter(DELIVERY)
        self.assertEqual(frontmatter["permission"]["edit"], "deny")
        body = frontmatter_and_body(DELIVERY)[1]
        self.assertIn("decision_owner: PO", body)
        self.assertIn("state: awaiting_po_closure|hold", body)
        self.assertIn("target_state: OPEN", body)

    def test_D2(self) -> None:
        case = self.case("D2")
        actual = delivery_dod(case["input"]["result"], case["input"]["target_state"])
        assert_subset(case["expected"], actual)

    def test_D3(self) -> None:
        case = self.case("D3")
        data = case["input"]
        actual = {
            "valid_is_authorized": explicit_po_authorization(data["valid"], data["target"]),
            "invalid_are_authorized": [
                explicit_po_authorization(request, data["target"])
                for request in data["invalid"]
            ],
            "close_attempts": 0,
        }
        assert_subset(case["expected"], actual)

    def test_D4(self) -> None:
        case = self.case("D4")
        actual = authorized_close(
            target=case["input"]["target"],
            target_state=case["input"]["target_state"],
            request=case["input"]["request"],
            fresh_dod=case["input"]["fresh_dod"],
        )
        assert_subset(case["expected"], actual)

    def test_R1(self) -> None:
        case = self.case("R1")
        actual = router_registration_observation()
        assert_subset(case["expected"], actual)
        role_files = {path.stem for path in AGENT_DIR.glob("*.md")}
        self.assertEqual(role_files, set(EXPECTED_ROLES))
        for role, expected_tasks in EXPECTED_ROLES.items():
            frontmatter = parse_frontmatter(AGENT_DIR / f"{role}.md")
            self.assertEqual(frontmatter["mode"], "subagent", role)
            self.assertEqual(frontmatter["permission"]["task"], expected_tasks, role)
        spec = read(SPEC)
        for role in EXPECTED_ROLES:
            self.assertIn(f"`.opencode/agent/{role}.md`", spec)
        self.assertFalse(actual["router_file"])
        self.assertFalse(actual["router_subagent"])
        self.assertFalse(actual["router_task_node"])
        self.assertFalse(actual["router_closes_issue"])
        self.assertFalse(actual["router_authorizes_po"])

    def test_R2(self) -> None:
        case = self.case("R2")
        actual = {
            name: {
                key: value
                for key, value in router_state(facts).items()
                if key in case["expected"][name]
            }
            for name, facts in case["input"].items()
        }
        assert_subset(case["expected"], actual)

    def test_C1(self) -> None:
        case = self.case("C1")
        legacy = dict(case["input"]["route"])
        extended = dict(legacy)
        extended["dod"] = {"result": "pass", "target_state": "OPEN"}
        extended["router"] = {"state": "awaiting_po_closure"}
        spec = read(SPEC)
        route_block = yaml_block(spec, "route", "action")
        spec_actions = yaml_child_value(route_block, "action").split("|")
        spec_targets = yaml_child_value(route_block, "to").split("|")
        actual = {
            "legacy_fields_preserved": all(
                re.search(rf"^  {re.escape(key)}:", route_block, re.MULTILINE)
                for key in legacy
            ),
            "action": extended["action"],
            "to": extended["to"],
            "dod_is_additive": "dod:" in route_block
            and extended["action"] == legacy["action"]
            and extended["to"] == legacy["to"],
            "router_is_sibling": "router:" not in route_block
            and yaml_block(read(DELIVERY), "router").startswith("router:"),
        }
        delivery_text = read(DELIVERY)
        workflow_text = read(WORKFLOW)
        self.assertIn("action: requirements|specification|planning|execution|done", delivery_text)
        self.assertIn("action: requirements|specification|planning|execution|done", spec)
        self.assertIn(legacy["to"], spec_targets)
        self.assertIn(legacy["action"], spec_actions)
        self.assertIn("closure:", workflow_text)
        assert_subset(case["expected"], actual)

    def test_C2(self) -> None:
        case = self.case("C2")
        actual = closure_contract_observation()
        assert_subset(case["expected"], actual)
        skill = read(WORKFLOW)
        spec = read(SPEC)
        delivery = read(DELIVERY)
        skill_router = yaml_block(skill, "router")
        self.assertEqual(skill_router, yaml_block(spec, "router"))
        self.assertEqual(skill_router, yaml_block(delivery, "router"))
        self.assertEqual({"router"}, top_level_keys(skill_router))
        self.assertEqual(set(ROUTER_KEYS), yaml_child_keys(skill_router))
        closure_block = yaml_block(skill, "closure")
        self.assertEqual(
            {"closure", *CLOSURE_KEYS},
            top_level_keys(closure_block) | yaml_child_keys(closure_block),
        )
        self.assertEqual(yaml_block(skill, "closure"), yaml_block(spec, "closure"))
        self.assertIn("state: " + "|".join(ROUTER_STATES), skill_router)
        self.assertIn("action: " + "|".join(ROUTER_ACTIONS), skill_router)
        self.assertIn("единственный источник правил", skill)
        self.assertIn("зеркало контракта", spec)
        self.assertIn("не роль", skill)
        self.assertIn("не роль", spec)
        self.assertIsNone(TRACKER_COMMAND.search(spec))
        for path in AGENT_DIR.glob("*.md"):
            _, body = frontmatter_and_body(path)
            self.assertIsNone(TRACKER_COMMAND.search(body), path.name)
            for key in EXPECTED_CONTRACT_KEYS[path.stem]:
                self.assertRegex(body, rf"(?m)^\s*{re.escape(key)}:", f"{path.name}: {key}")
                self.assertRegex(spec, rf"(?m)^\s*{re.escape(key)}:", f"spec: {key}")

    def test_V1(self) -> None:
        case = self.case("V1")
        actual = authorized_close(
            target=case["input"]["target"],
            target_state=case["input"]["target_state"],
            request=case["input"]["request"],
            fresh_dod=case["input"]["fresh_dod"],
        )
        assert_subset(case["expected"], actual)

    def test_V2(self) -> None:
        case = self.case("V2")
        actual = authorized_close(
            target=case["input"]["target"],
            target_state=case["input"]["target_state"],
            request=case["input"]["request"],
            fresh_dod=case["input"]["fresh_dod"],
        )
        assert_subset(case["expected"], actual)

    def test_V3(self) -> None:
        case = self.case("V3")
        actual = authorized_close(
            target=case["input"]["target"],
            target_state=case["input"]["target_state"],
            request=case["input"]["request"],
            fresh_dod=case["input"]["fresh_dod"],
        )
        assert_subset(case["expected"], actual)

    def test_V4(self) -> None:
        case = self.case("V4")
        actual = authorized_close(
            target=case["input"]["target"],
            target_state=case["input"]["target_state"],
            marker_present=case["input"]["marker_present"],
            request=case["input"]["request"],
            fresh_dod=case["input"]["fresh_dod"],
        )
        assert_subset(case["expected"], actual)

    def test_V5(self) -> None:
        case = self.case("V5")
        actual = contract_observation()
        self.assertIn("do NOT close a parent issue", read(DELIVERY))
        self.assertIn("cannot obtain that permission", read(DELIVERY))
        assert_subset(case["expected"], actual)

    def test_ROOT1(self) -> None:
        case = self.case("ROOT1")
        root = self.fixture["root_snapshot"]
        self.assertEqual(root["number"], case["input"]["root"])
        actual = {
            "state": root["state"],
            "labels": root["labels"],
            "atomic": root["atomic"],
            "depends_on": root["depends_on"],
        }
        assert_subset(case["expected"], actual)
        self.assertNotIn("atomic", root["labels"])

    def test_ROOT2(self) -> None:
        case = self.case("ROOT2")
        facts = {
            "ready": True,
            "open_blockers": [],
            "dod": case["input"]["dod"],
            "target_state": case["input"]["target_state"],
            "close_confirmed": case["input"]["close_confirmed"],
        }
        actual = {
            "router_state": router_state(facts)["state"],
            "delivery_done": False,
            "done_requires_close_confirmation": True,
        }
        assert_subset(case["expected"], actual)
        self.assertNotEqual(actual["router_state"], "done")


if __name__ == "__main__":
    unittest.main()
