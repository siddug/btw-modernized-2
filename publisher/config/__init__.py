"""Target module ``config`` (design name ``config``, build order 0).

Source modules absorbed: ``constants``, ``utils``. Depends on: nothing.

Responsibilities (from the approved system design):

* Single settings object loaded once from the environment / ``.env`` with the
  exact source names and defaults: ``PORT`` (default ``9222``), ``NODE_ENV``,
  ``DEBUG``, ``ROOT_DOMAIN``, ``DOMAIN_QUERY_PARAM``, ``HTTPS_DOMAIN``,
  ``UMAMI_SOURCE``, ``TASKS_URL`` (default ``http://localhost:9210``),
  ``TASKS_DATABASE_URL``, ``ADMIN_SLUG``, ``TURN_OFF_SINGLE_USER_MODE``.
* ``constants.js`` maps to configuration only: ``GHOST_URL`` and
  ``BLOG_CATEGORIES`` (order ``['blog','product','help','guides']``) are kept
  as config, while ``GHOST_API_KEY`` is read from the env/secret store and is
  never copied into this repository (ADR-003).
* JS numeric-string coercions (``Number('') === 0`` falsy, ``Number('1')``
  truthy, ``NaN`` falsy) are reproduced by one ``env_flag``-style helper used
  identically at every use site (DEBUG, HTTPS_DOMAIN, TURN_OFF_SINGLE_USER_MODE).

Implementation (feature ``config-settings``):

* ``Settings`` — a single pydantic-settings ``BaseSettings`` subclass — is the
  one settings object, instantiated exactly once at import time as the
  module-level ``settings`` singleton; ``get_settings()`` returns that same
  object (FastAPI dependency-injection hook). It reads the process environment
  and an optional ``.env`` file in the working directory (the pm2 / Docker
  deployment configs) using the exact source env names above.
* The two source defaults are the JS ``||`` expressions ``process.env.PORT ||
  "9222"`` (bin/www) and ``process.env.TASKS_URL || 'http://localhost:9210'``
  (routes/index.js): they apply when the variable is unset **or empty**, which
  the ``PORT`` / ``TASKS_URL`` validators reproduce exactly.
* ``env_flag(name)`` reproduces ``!!Number(process.env[name])`` as an int with
  the approved coercion table — missing -> ``NaN`` -> 0, ``''`` -> 0,
  unparseable (e.g. ``'abc'``) -> ``NaN`` -> 0, ``'0'`` -> 0, ``'1'`` -> 1 —
  so every use site can write ``if env_flag("DEBUG"):`` mirroring the source's
  ``if (!!Number(process.env.DEBUG)):``. It reads ``os.environ`` live (the
  source reads ``process.env`` at each use site) and falls back to the
  once-loaded ``settings`` for values that arrived only via ``.env``.
* All modules read ``settings.X``; nothing else in the port reads
  ``os.environ`` for these names.

``constants.js`` absorbed as configuration only (ADR-003):

* ``GHOST_URL`` and ``BLOG_CATEGORIES`` are preserved as config keys with the
  recorded source values carried by ``.env.example``
  (``GHOST_URL=https://blog-admin.btw.so``,
  ``BLOG_CATEGORIES=blog,product,help,guides``); the ordered default
  ``['blog', 'product', 'help', 'guides']`` is kept verbatim in
  ``DEFAULT_BLOG_CATEGORIES`` and the comma-separated ``.env`` form is parsed
  back into that order.
* ``GHOST_API_KEY`` resolves only via the environment / secret store: the field
  has no default and the credential literal from the source ``constants.js``
  is deliberately absent from every file of this repository
  (``scripts/smoke.py`` scans for it).

Dead-code drops recorded here (ADR-010):

* ``utils/utils.js`` was a single ``module.exports = {};`` statement with zero
  require sites anywhere in the app — dead code with no runtime behaviour —
  and is intentionally not ported.
"""

from __future__ import annotations

import json
import os
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

__all__ = [
    "DEFAULT_BLOG_CATEGORIES",
    "DEFAULT_PORT",
    "DEFAULT_TASKS_URL",
    "Settings",
    "env_flag",
    "get_settings",
    "settings",
]

#: ``bin/www`` default: ``process.env.PORT || "9222"`` (kept as the raw string;
#: the ``normalizePort`` tri-state belongs to the ``server`` module, ADR-009).
DEFAULT_PORT = "9222"

#: ``routes/index.js`` default: ``process.env.TASKS_URL || 'http://localhost:9210'``.
DEFAULT_TASKS_URL = "http://localhost:9210"

#: Blog category slugs preserved verbatim (and in order) from the source
#: ``constants.js`` ``BLOG_CATEGORIES`` literal.
DEFAULT_BLOG_CATEGORIES = ["blog", "product", "help", "guides"]


class Settings(BaseSettings):
    """Env-driven settings for the publisher port, loaded once from env/``.env``.

    Field names are the exact source ``process.env`` names; every value is kept
    as the raw string the JS app saw (flag semantics stay at the use sites via
    :func:`env_flag`). ``GHOST_API_KEY`` is secret-store only (ADR-003) and
    never has a code default.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PORT: str = DEFAULT_PORT
    NODE_ENV: str | None = None
    DEBUG: str | None = None
    ROOT_DOMAIN: str | None = None
    DOMAIN_QUERY_PARAM: str | None = None
    HTTPS_DOMAIN: str | None = None
    UMAMI_SOURCE: str | None = None
    TASKS_URL: str = DEFAULT_TASKS_URL
    TASKS_DATABASE_URL: str | None = None
    ADMIN_SLUG: str | None = None
    TURN_OFF_SINGLE_USER_MODE: str | None = None
    # constants.js absorbed as configuration only (ADR-003); the recorded
    # source values are carried by .env.example, not by code literals.
    GHOST_URL: str | None = None
    # Secret store only: never a default, never a literal in this repo.
    GHOST_API_KEY: str | None = None
    # NoDecode lets the raw "blog,product,help,guides" string from env/.env
    # reach the validator instead of pydantic-settings' JSON decoding.
    BLOG_CATEGORIES: Annotated[list[str], NoDecode] = list(DEFAULT_BLOG_CATEGORIES)

    @field_validator("PORT", "TASKS_URL", mode="before")
    @classmethod
    def _empty_string_is_unset(cls, v: Any, info: Any) -> Any:
        # JS ``process.env.X || default`` also falls back on the empty string.
        if v is None or v == "":
            return DEFAULT_PORT if info.field_name == "PORT" else DEFAULT_TASKS_URL
        return v

    @field_validator("BLOG_CATEGORIES", mode="before")
    @classmethod
    def _parse_blog_categories(cls, v: Any) -> Any:
        if isinstance(v, str):
            text = v.strip()
            if text.startswith("["):
                try:
                    decoded = json.loads(text)
                except ValueError:
                    decoded = None
                if isinstance(decoded, list):
                    return decoded
            return [part.strip() for part in text.split(",") if part.strip()]
        return v


#: The single settings object, loaded once at import time from the environment
#: and ``.env`` (mirrors how the Node app sees ``process.env`` after pm2/Docker
#: have applied their env files).
settings = Settings()


def get_settings() -> Settings:
    """Return the process-wide :data:`settings` singleton (DI hook)."""
    return settings


def _raw_env_value(name: str) -> str | None:
    """Effective raw value for ``name``.

    ``os.environ`` is read live first (the source reads ``process.env`` at each
    use site, not at require time); values that arrived only through ``.env``
    are taken from the once-loaded :data:`settings`.
    """
    if name in os.environ:
        return os.environ[name]
    return getattr(settings, name, None)


def env_flag(name: str) -> int:
    """Reproduce the source's ``!!Number(process.env[name])`` as an ``int``.

    Approved coercion table (JS ``Number`` semantics, enumerated in the mapping
    plan): missing -> ``NaN`` -> ``0``; ``''`` -> ``0``; unparseable such as
    ``'abc'`` -> ``NaN`` -> ``0``; ``'0'`` -> ``0``; ``'1'`` -> ``1`` (truthy).
    Use sites write ``if env_flag("DEBUG"):`` exactly where the source wrote
    ``if (!!Number(process.env.DEBUG)):`` (DEBUG, HTTPS_DOMAIN,
    TURN_OFF_SINGLE_USER_MODE).
    """
    raw = _raw_env_value(name)
    if raw is None:
        return 0
    try:
        return int(str(raw))
    except ValueError:
        return 0
