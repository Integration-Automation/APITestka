"""
Reference AI backend on the Anthropic API (``pip install je_api_testka[ai]``).

:class:`AnthropicAIBackend` sends each :meth:`~AnthropicAIBackend.complete`
call as one Messages API request and returns the reply text.

* Credentials come from the environment the ``anthropic`` SDK reads
  (``ANTHROPIC_API_KEY``, ``ANTHROPIC_AUTH_TOKEN`` or an ``ant auth login``
  profile); the backend never takes or stores a key.
* The default model is ``claude-opus-5-5``. Its thinking is always on, so depth
  is set with ``effort`` (``low`` to ``max``); the backend sends ``medium``
  explicitly unless told otherwise.
* Server-side refusal fallbacks are on (``fallbacks="default"``): when a safety
  classifier declines, the API re-runs the request on the fallback model
  Anthropic recommends for that refusal category. Pass ``fallbacks=None`` to
  turn it off.
* A refusal, a truncated reply (``max_tokens``), a rate limit, a server error
  or a network failure returns ``""``, so the caller uses its deterministic
  fallback; the SDK already retried the transient ones. A rejected request
  (bad key, unknown model, invalid parameter) raises
  :class:`APIAIBackendException`, because retrying cannot fix it.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional

from je_api_testka.ai.backend import AIBackend
from je_api_testka.utils.exception.exceptions import APIAIBackendException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

if TYPE_CHECKING:  # the SDK is optional; imported for annotations only
    import anthropic

DEFAULT_ANTHROPIC_MODEL: str = "claude-opus-5-5"
DEFAULT_ANTHROPIC_EFFORT: str = "medium"
DEFAULT_ANTHROPIC_MAX_TOKENS: int = 16000
DEFAULT_FALLBACKS: str = "default"
FALLBACK_BETA: str = "server-side-fallback-2026-07-01"
ANTHROPIC_MISSING: str = "anthropic is not installed. Install with `pip install je_api_testka[ai]`."
_SERVER_ERROR_STATUS: int = 500

SYSTEM_PROMPT: str = (
    "You are the text-completion backend of APITestka, an API testing framework. "
    "Each request asks for one artefact, such as executor actions, a JSON value that satisfies a schema, "
    "or labels for failed requests; the request explains the format and any context follows in a "
    "<context> block. Reply with the artefact only. When JSON is asked for, reply with exactly one JSON "
    "value, without explanations and without Markdown code fences."
)


def _import_anthropic():
    try:
        import anthropic  # type: ignore
    except ImportError as error:
        raise APIAIBackendException(ANTHROPIC_MISSING) from error
    return anthropic


def _user_message(prompt: str, context: Optional[dict]) -> str:
    if not context:
        return prompt
    # sort_keys keeps identical contexts byte-identical, which keeps them cacheable.
    rendered = json.dumps(context, sort_keys=True, ensure_ascii=False, default=str)
    return f"{prompt}\n\n<context>\n{rendered}\n</context>"


def _reply_text(response: Any) -> str:
    return "".join(block.text for block in response.content if getattr(block, "type", "") == "text")


@dataclass
class AnthropicAIBackend(AIBackend):
    """
    :class:`AIBackend` on the Anthropic Messages API.

    :param model: model ID (default ``claude-opus-5-5``).
    :param effort: ``output_config.effort`` (``low``, ``medium``, ``high``, ``xhigh``, ``max``); ``None`` omits it.
    :param max_tokens: output cap per reply, thinking included.
    :param fallbacks: server-side refusal fallback mode; ``None`` turns it off.
    :param timeout: request timeout in seconds; ``None`` keeps the SDK default.
    :param client: a ready ``anthropic.Anthropic`` client (tests, proxies); built on first use when ``None``.
    """

    model: str = DEFAULT_ANTHROPIC_MODEL
    effort: Optional[str] = DEFAULT_ANTHROPIC_EFFORT
    max_tokens: int = DEFAULT_ANTHROPIC_MAX_TOKENS
    fallbacks: Optional[str] = DEFAULT_FALLBACKS
    timeout: Optional[float] = None
    client: Optional["anthropic.Anthropic"] = None

    def _client(self) -> "anthropic.Anthropic":
        if self.client is None:
            anthropic = _import_anthropic()
            options = {} if self.timeout is None else {"timeout": self.timeout}
            self.client = anthropic.Anthropic(**options)
        return self.client

    def request_options(self, prompt: str, context: Optional[dict] = None) -> dict:
        """Return the keyword arguments :meth:`complete` passes to ``client.beta.messages.create``."""
        options: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": _user_message(prompt, context)}],
        }
        if self.effort:
            options["output_config"] = {"effort": self.effort}
        betas: List[str] = []
        if self.fallbacks:
            options["fallbacks"] = self.fallbacks
            betas.append(FALLBACK_BETA)
        if betas:
            options["betas"] = betas
        return options

    def complete(self, prompt: str, *, context: Optional[dict] = None) -> str:
        """Return the model's reply text, or ``""`` when there is no usable reply (see the module notes)."""
        anthropic = _import_anthropic()
        try:
            response = self._client().beta.messages.create(**self.request_options(prompt, context))
        except anthropic.RateLimitError as error:
            apitestka_logger.error(f"AnthropicAIBackend rate limited after SDK retries: {error.message}")
            return ""
        except anthropic.APIStatusError as error:
            if error.status_code >= _SERVER_ERROR_STATUS:
                apitestka_logger.error(f"AnthropicAIBackend server error {error.status_code}: {error.message}")
                return ""
            raise APIAIBackendException(
                f"Anthropic API rejected the request ({error.status_code}): {error.message}") from error
        except anthropic.APIConnectionError as error:
            apitestka_logger.error(f"AnthropicAIBackend could not reach the API: {error!r}")
            return ""
        return self._usable_text(response)

    def _usable_text(self, response: Any) -> str:
        request_id = getattr(response, "_request_id", None)
        apitestka_logger.info(
            f"AnthropicAIBackend {getattr(response, 'model', self.model)} stop_reason={response.stop_reason} "
            f"request_id={request_id}")
        if response.stop_reason == "refusal":
            category = getattr(getattr(response, "stop_details", None), "category", None)
            apitestka_logger.error(f"AnthropicAIBackend: the request was declined (category {category})")
            return ""
        if response.stop_reason == "max_tokens":
            apitestka_logger.error(f"AnthropicAIBackend: reply cut off at max_tokens={self.max_tokens}")
            return ""
        return _reply_text(response)
