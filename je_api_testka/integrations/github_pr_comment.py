"""
GitHub PR auto-comment helper.

Builds a markdown summary of the current run and POSTs it as a comment on a
pull request. Authentication via personal access token or GitHub Actions'
``GITHUB_TOKEN``.
"""
from __future__ import annotations

from typing import Optional

import httpx

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.generate_report.markdown_report import render_markdown
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_PR_TIMEOUT_SECONDS: float = 15.0
GITHUB_API_BASE: str = "https://api.github.com"


def build_pr_comment_body(title: str = "APITestka run") -> str:
    """Wrap ``render_markdown`` output in a collapsed details block."""
    return (
        f"<details><summary>{title}</summary>\n\n"
        f"{render_markdown(title=title)}\n"
        "</details>"
    )


def post_pr_comment(
    repo: str,
    pr_number: int,
    token: str,
    body: Optional[str] = None,
    timeout: float = DEFAULT_PR_TIMEOUT_SECONDS,
    transport: Optional[object] = None,
) -> int:
    """POST a comment to ``https://api.github.com/repos/<repo>/issues/<pr>/comments``."""
    apitestka_logger.info(f"github_pr_comment post_pr_comment repo: {repo} pr: {pr_number}")
    if not repo or "/" not in repo:
        raise APITesterException("repo must be in 'owner/name' format")
    payload = {"body": body or build_pr_comment_body()}
    url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    client_kwargs = {"timeout": timeout}
    if transport is not None:
        client_kwargs["transport"] = transport
    with httpx.Client(**client_kwargs) as client:
        response = client.post(url, json=payload, headers=headers)
    return response.status_code
