"""
Optional schema-style assertions:

* :func:`check_json_schema` validates a payload against a JSON Schema document
  using the optional ``jsonschema`` package.
* :func:`check_jsonpath` matches values located by a JSONPath expression using
  the optional ``jsonpath-ng`` package.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional

from je_api_testka.utils.exception.exceptions import APIAssertException, APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

JSONSCHEMA_NOT_INSTALLED: str = (
    "jsonschema package is not installed. Install with `pip install jsonschema`."
)
JSONPATH_NOT_INSTALLED: str = (
    "jsonpath-ng package is not installed. Install with `pip install jsonpath-ng`."
)


def _import_jsonschema():
    try:
        import jsonschema  # type: ignore
        return jsonschema
    except ImportError as error:
        apitestka_logger.error(f"schema_check import jsonschema failed: {repr(error)}")
        raise APITesterException(JSONSCHEMA_NOT_INSTALLED) from error


def _import_jsonpath_ng():
    try:
        from jsonpath_ng import parse  # type: ignore
        return parse
    except ImportError as error:
        apitestka_logger.error(f"schema_check import jsonpath_ng failed: {repr(error)}")
        raise APITesterException(JSONPATH_NOT_INSTALLED) from error


def check_json_schema(payload: Any, schema: dict) -> None:
    """Raise :class:`APIAssertException` if ``payload`` does not satisfy ``schema``."""
    apitestka_logger.info(f"schema_check check_json_schema schema: {schema}")
    jsonschema = _import_jsonschema()
    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.ValidationError as error:
        message = f"json schema validation failed: {error.message}"
        apitestka_logger.error(message)
        raise APIAssertException(message) from error


def check_jsonpath(
    payload: Any,
    expression: str,
    expected: Optional[Any] = None,
    expected_in: Optional[Iterable[Any]] = None,
) -> list:
    """
    Evaluate ``expression`` against ``payload`` and optionally assert.

    * ``expected``: every match must equal this value.
    * ``expected_in``: every match must be one of these values.

    Returns the list of matched values for further use.
    """
    apitestka_logger.info(
        f"schema_check check_jsonpath expression: {expression} expected: {expected}"
    )
    parse = _import_jsonpath_ng()
    matches = [match.value for match in parse(expression).find(payload)]
    if not matches:
        message = f"jsonpath {expression} matched nothing"
        apitestka_logger.error(message)
        raise APIAssertException(message)
    if expected is not None:
        for value in matches:
            if value != expected:
                message = f"jsonpath {expression} expected {expected} but got {value}"
                apitestka_logger.error(message)
                raise APIAssertException(message)
    if expected_in is not None:
        allowed = list(expected_in)
        for value in matches:
            if value not in allowed:
                message = f"jsonpath {expression} value {value} not in {allowed}"
                apitestka_logger.error(message)
                raise APIAssertException(message)
    return matches
