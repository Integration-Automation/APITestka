"""
Compare an actual response with a contract's expected response (Pact v2 rules).

Without a rule, values must be equal. A rule applies to its path and everything
below it, and the most specific rule wins. Paths look like ``$.body.items[*].id``,
where ``[*]`` and ``.*`` match any index or key.

* ``{"match": "type"}``: same JSON type (numbers are one type). Under a type rule
  every element of an actual array must match the first expected element, and
  ``"min"`` sets the minimum length.
* ``{"match": "regex", "regex": "..."}``: the value's text must fully match.

Objects may carry keys the contract does not mention, as in Pact.
"""
from __future__ import annotations

import re
from typing import Any, List, Mapping, Optional, Sequence

RuleMap = Mapping[str, Mapping[str, Any]]

_TOKEN = re.compile(r"\['([^']*)'\]|\[(\*|\d+)\]|\.?([^.\[\]]+)")
_EQUALITY: str = "equality"


def _pattern_tokens(pattern: str) -> List[str]:
    return [quoted or index or plain for quoted, index, plain in _TOKEN.findall(pattern)]


def _render(tokens: Sequence[str]) -> str:
    text = tokens[0]
    for token in tokens[1:]:
        text += f"[{token}]" if token.isdigit() else f".{token}"
    return text


def _rule_for(tokens: Sequence[str], rules: RuleMap) -> Optional[Mapping[str, Any]]:
    best: Optional[Mapping[str, Any]] = None
    best_length = -1
    for pattern, rule in rules.items():
        pattern_tokens = _pattern_tokens(pattern)
        if len(pattern_tokens) > len(tokens) or len(pattern_tokens) <= best_length:
            continue
        # The pattern may be shorter than the path: a rule covers everything below it.
        if all(expected in ("*", actual) for expected, actual in zip(pattern_tokens, tokens, strict=False)):
            best, best_length = rule, len(pattern_tokens)
    return best


def json_type(value: Any) -> str:
    """Return the JSON type name of ``value`` (``number`` for int and float, ``boolean`` for bool)."""
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "null" if value is None else type(value).__name__


class _Matcher:
    def __init__(self, rules: RuleMap) -> None:
        self.rules = rules
        self.mismatches: List[str] = []

    def compare(self, expected: Any, actual: Any, tokens: List[str]) -> None:
        rule = _rule_for(tokens, self.rules) or {}
        kind = rule.get("match", _EQUALITY)
        if kind == "regex":
            self._regex(rule, actual, tokens)
        elif isinstance(expected, dict):
            self._object(expected, actual, tokens)
        elif isinstance(expected, list):
            self._array(expected, actual, tokens, rule, kind)
        elif kind == "type":
            self._same_type(expected, actual, tokens)
        elif expected != actual or json_type(expected) != json_type(actual):
            self.mismatches.append(f"{_render(tokens)}: expected {expected!r}, got {actual!r}")

    def _regex(self, rule: Mapping[str, Any], actual: Any, tokens: List[str]) -> None:
        if actual is None or not re.fullmatch(str(rule.get("regex", "")), str(actual)):
            self.mismatches.append(f"{_render(tokens)}: {actual!r} does not match /{rule.get('regex')}/")

    def _same_type(self, expected: Any, actual: Any, tokens: List[str]) -> None:
        if json_type(expected) != json_type(actual):
            self.mismatches.append(
                f"{_render(tokens)}: expected a {json_type(expected)}, got {json_type(actual)} {actual!r}")

    def _object(self, expected: dict, actual: Any, tokens: List[str]) -> None:
        if not isinstance(actual, dict):
            self.mismatches.append(f"{_render(tokens)}: expected an object, got {json_type(actual)}")
            return
        for key, value in expected.items():
            if key not in actual:
                self.mismatches.append(f"{_render([*tokens, key])}: missing")
            else:
                self.compare(value, actual[key], [*tokens, key])

    def _array(self, expected: list, actual: Any, tokens: List[str], rule: Mapping[str, Any], kind: str) -> None:
        if not isinstance(actual, list):
            self.mismatches.append(f"{_render(tokens)}: expected an array, got {json_type(actual)}")
            return
        minimum = rule.get("min")
        if isinstance(minimum, int) and len(actual) < minimum:
            self.mismatches.append(f"{_render(tokens)}: expected at least {minimum} items, got {len(actual)}")
        if kind == "type":
            for index, item in enumerate(actual if expected else []):
                self.compare(expected[0], item, [*tokens, str(index)])
            return
        if len(expected) != len(actual):
            self.mismatches.append(f"{_render(tokens)}: expected {len(expected)} items, got {len(actual)}")
            return
        for index, (want, got) in enumerate(zip(expected, actual, strict=True)):
            self.compare(want, got, [*tokens, str(index)])


def body_mismatches(expected: Any, actual: Any, rules: Optional[RuleMap] = None) -> List[str]:
    """Return why ``actual`` does not satisfy the expected body under ``rules`` (empty when it does)."""
    matcher = _Matcher(rules or {})
    matcher.compare(expected, actual, ["$", "body"])
    return matcher.mismatches


def _media_type(value: str) -> str:
    return value.split(";", 1)[0].strip().lower()


def header_mismatches(expected: Mapping[str, str], actual: Mapping[str, str],
                      rules: Optional[RuleMap] = None) -> List[str]:
    """
    Return why ``actual`` headers do not satisfy ``expected`` (names compare case-insensitively).

    Without a rule, ``Content-Type`` compares the media type only, so a ``charset`` parameter does not matter.
    """
    lowered = {str(name).lower(): str(value) for name, value in actual.items()}
    mismatches: List[str] = []
    for name, want in expected.items():
        tokens = ["$", "headers", name]
        got = lowered.get(name.lower())
        rule = _rule_for(tokens, rules or {})
        if got is None:
            mismatches.append(f"{_render(tokens)}: missing")
        elif rule and rule.get("match") == "regex":
            if not re.fullmatch(str(rule.get("regex", "")), got):
                mismatches.append(f"{_render(tokens)}: {got!r} does not match /{rule.get('regex')}/")
        elif name.lower() == "content-type":
            if _media_type(got) != _media_type(want):
                mismatches.append(f"{_render(tokens)}: expected {want!r}, got {got!r}")
        elif got.strip() != str(want).strip():
            mismatches.append(f"{_render(tokens)}: expected {want!r}, got {got!r}")
    return mismatches
