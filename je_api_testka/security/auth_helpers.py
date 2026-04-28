"""
Authentication header helpers.

* Basic Auth and Bearer token are stdlib-only.
* JWT signing requires the optional ``PyJWT`` package.
* AWS SigV4 signing requires the optional ``botocore`` package.
"""
from __future__ import annotations

import base64
from typing import Optional

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

PYJWT_NOT_INSTALLED: str = "PyJWT not installed. Install with `pip install pyjwt`."
BOTOCORE_NOT_INSTALLED: str = "botocore not installed. Install with `pip install botocore`."
DEFAULT_JWT_ALGORITHM: str = "HS256"


def basic_auth_header(username: str, password: str) -> dict:
    """Return ``{'Authorization': 'Basic <token>'}`` for HTTP basic auth."""
    if not isinstance(username, str) or not isinstance(password, str):
        raise APITesterException("basic_auth_header requires string credentials")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def bearer_token_header(token: str) -> dict:
    """Return ``{'Authorization': 'Bearer <token>'}``."""
    if not isinstance(token, str) or not token:
        raise APITesterException("bearer_token_header requires a non-empty token")
    return {"Authorization": f"Bearer {token}"}


def build_jwt(payload: dict, secret: str, algorithm: str = DEFAULT_JWT_ALGORITHM) -> str:
    """Return a signed JWT string. Requires PyJWT."""
    apitestka_logger.info(f"auth_helpers build_jwt algorithm: {algorithm}")
    try:
        import jwt  # type: ignore
    except ImportError as error:
        raise APITesterException(PYJWT_NOT_INSTALLED) from error
    return jwt.encode(payload, secret, algorithm=algorithm)


def aws_sigv4_headers(
    method: str,
    url: str,
    region: str,
    service: str,
    access_key: str,
    secret_key: str,
    body: Optional[bytes] = None,
    extra_headers: Optional[dict] = None,
) -> dict:
    """Sign a request with AWS SigV4 and return the resulting headers."""
    apitestka_logger.info(f"auth_helpers aws_sigv4_headers service: {service} region: {region}")
    try:
        from botocore.auth import SigV4Auth  # type: ignore
        from botocore.awsrequest import AWSRequest  # type: ignore
        from botocore.credentials import Credentials  # type: ignore
    except ImportError as error:
        raise APITesterException(BOTOCORE_NOT_INSTALLED) from error
    request = AWSRequest(method=method.upper(), url=url, data=body or b"")
    if extra_headers:
        for key, value in extra_headers.items():
            request.headers[key] = value
    credentials = Credentials(access_key=access_key, secret_key=secret_key)
    SigV4Auth(credentials, service, region).add_auth(request)
    return dict(request.headers.items())
