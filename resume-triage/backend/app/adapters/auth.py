"""Auth module placeholder for future ATS/source integrations (§6).

OAuth 2.0 flows (client-credentials for Workday RaaS; 3-legged for LinkedIn
RSC) will live here. Secrets are read from environment variables ONLY and are
never committed. This is a seam, not a working implementation.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class OAuthCredentials:
    client_id: str
    client_secret: str
    token_url: str


def load_credentials(prefix: str) -> OAuthCredentials:
    """Load credentials for a vendor from env vars, e.g. prefix='WORKDAY'.

    Expects WORKDAY_CLIENT_ID / WORKDAY_CLIENT_SECRET / WORKDAY_TOKEN_URL.
    """
    return OAuthCredentials(
        client_id=os.environ.get(f"{prefix}_CLIENT_ID", ""),
        client_secret=os.environ.get(f"{prefix}_CLIENT_SECRET", ""),
        token_url=os.environ.get(f"{prefix}_TOKEN_URL", ""),
    )


def fetch_access_token(creds: OAuthCredentials) -> str:  # pragma: no cover - future
    """TODO: perform the OAuth grant and return a bearer token.

    client-credentials (Workday) vs authorization-code/3-legged (LinkedIn) are
    selected per adapter at integration time."""
    raise NotImplementedError("OAuth token exchange is a future integration seam.")
