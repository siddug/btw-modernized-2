"""Focused tests for the ``config`` target module (feature ``config-settings``).

Run from the target root: ``python3 -m pytest tests/ -q``

Covers the feature's acceptance criteria:

* settings load from env with ``PORT||9222`` and ``TASKS_URL||'http://localhost:9210'``
  defaults applied exactly when unset (and, like the JS ``||``, when empty);
* ``GHOST_API_KEY`` resolves only via env/secret store and its leaked source
  literal appears in no file of the port (ADR-003);
* the ``utils/utils.js`` dead-code drop is recorded in the module docstring
  (ADR-010);
* the recorded scenario environment (``DEBUG=1``, ``DOMAIN_QUERY_PARAM='domain'``)
  loads through the module, with ``env_flag`` reproducing the JS
  ``!!Number(process.env.X)`` coercions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import publisher.config as config
from publisher.config import (
    DEFAULT_BLOG_CATEGORIES,
    DEFAULT_PORT,
    DEFAULT_TASKS_URL,
    Settings,
    env_flag,
    get_settings,
    settings,
)

ROOT = Path(__file__).resolve().parent.parent

CONFIG_ENV_KEYS = [
    "PORT",
    "NODE_ENV",
    "DEBUG",
    "ROOT_DOMAIN",
    "DOMAIN_QUERY_PARAM",
    "HTTPS_DOMAIN",
    "UMAMI_SOURCE",
    "TASKS_URL",
    "TASKS_DATABASE_URL",
    "ADMIN_SLUG",
    "TURN_OFF_SINGLE_USER_MODE",
    "GHOST_URL",
    "GHOST_API_KEY",
    "BLOG_CATEGORIES",
]


@pytest.fixture
def clean_env(monkeypatch):
    """Remove every config env var so defaults can be observed."""
    for key in CONFIG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


# --- defaults and env loading -------------------------------------------------


def test_defaults_applied_exactly_when_unset(clean_env):
    s = Settings(_env_file=None)
    assert s.PORT == "9222" == DEFAULT_PORT
    assert s.TASKS_URL == "http://localhost:9210" == DEFAULT_TASKS_URL
    assert s.NODE_ENV is None
    assert s.DEBUG is None
    assert s.ROOT_DOMAIN is None
    assert s.DOMAIN_QUERY_PARAM is None
    assert s.HTTPS_DOMAIN is None
    assert s.UMAMI_SOURCE is None
    assert s.TASKS_DATABASE_URL is None
    assert s.ADMIN_SLUG is None
    assert s.TURN_OFF_SINGLE_USER_MODE is None
    assert s.GHOST_URL is None
    assert s.GHOST_API_KEY is None
    assert s.BLOG_CATEGORIES == ["blog", "product", "help", "guides"]


def test_empty_string_env_falls_back_like_js_or(clean_env):
    # process.env.PORT || "9222" and process.env.TASKS_URL || '...' treat ''
    # as unset too, not only missing variables.
    clean_env.setenv("PORT", "")
    clean_env.setenv("TASKS_URL", "")
    s = Settings(_env_file=None)
    assert s.PORT == "9222"
    assert s.TASKS_URL == "http://localhost:9210"


def test_env_overrides_win(clean_env):
    clean_env.setenv("PORT", "8080")
    clean_env.setenv("NODE_ENV", "production")
    clean_env.setenv("DEBUG", "1")
    clean_env.setenv("ROOT_DOMAIN", "localhost:9222")
    clean_env.setenv("DOMAIN_QUERY_PARAM", "domain")
    clean_env.setenv("HTTPS_DOMAIN", "0")
    clean_env.setenv("UMAMI_SOURCE", "https://umami.example/script.js")
    clean_env.setenv("TASKS_URL", "http://tasks.internal:9210")
    clean_env.setenv("TASKS_DATABASE_URL", "postgres://u:p@db:5432/btw")
    clean_env.setenv("ADMIN_SLUG", "dev")
    clean_env.setenv("TURN_OFF_SINGLE_USER_MODE", "0")
    clean_env.setenv("GHOST_URL", "https://blog-admin.btw.so")
    clean_env.setenv("GHOST_API_KEY", "from-secret-store")
    s = Settings(_env_file=None)
    assert s.PORT == "8080"
    assert s.NODE_ENV == "production"
    assert s.DEBUG == "1"
    assert s.ROOT_DOMAIN == "localhost:9222"
    assert s.DOMAIN_QUERY_PARAM == "domain"
    assert s.HTTPS_DOMAIN == "0"
    assert s.UMAMI_SOURCE == "https://umami.example/script.js"
    assert s.TASKS_URL == "http://tasks.internal:9210"
    assert s.TASKS_DATABASE_URL == "postgres://u:p@db:5432/btw"
    assert s.ADMIN_SLUG == "dev"
    assert s.TURN_OFF_SINGLE_USER_MODE == "0"
    assert s.GHOST_URL == "https://blog-admin.btw.so"
    assert s.GHOST_API_KEY == "from-secret-store"


def test_dotenv_file_is_loaded_and_env_beats_dotenv(clean_env, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "PORT=7777\nTASKS_URL=http://dotenv-tasks:9210\nDEBUG=1\n"
        "DOMAIN_QUERY_PARAM=domain\nBLOG_CATEGORIES=blog,product,help,guides\n",
        encoding="utf-8",
    )
    s = Settings(_env_file=env_file)
    assert s.PORT == "7777"
    assert s.TASKS_URL == "http://dotenv-tasks:9210"
    assert s.DEBUG == "1"
    assert s.DOMAIN_QUERY_PARAM == "domain"
    assert s.BLOG_CATEGORIES == ["blog", "product", "help", "guides"]

    clean_env.setenv("PORT", "8080")  # real environment wins over .env
    assert Settings(_env_file=env_file).PORT == "8080"


def test_blog_categories_comma_separated_env_and_order(clean_env):
    clean_env.setenv("BLOG_CATEGORIES", "guides,help,product,blog")
    assert Settings(_env_file=None).BLOG_CATEGORIES == ["guides", "help", "product", "blog"]
    assert DEFAULT_BLOG_CATEGORIES == ["blog", "product", "help", "guides"]


def test_settings_singleton_is_loaded_once():
    assert settings is get_settings()
    assert isinstance(settings, Settings)


# --- env_flag: the JS !!Number(process.env.X) coercions ------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, 0),      # missing -> Number(undefined) = NaN -> falsy
        ("", 0),        # Number('') === 0 -> falsy
        ("0", 0),
        ("1", 1),       # truthy
        ("2", 2),       # truthy
        ("-1", -1),     # truthy
        ("abc", 0),     # NaN -> falsy
        (" 1 ", 1),     # whitespace-trimmed like Number(' 1 ')
    ],
)
def test_env_flag_coercion_table(clean_env, raw, expected):
    if raw is None:
        clean_env.delenv("DEBUG", raising=False)
    else:
        clean_env.setenv("DEBUG", raw)
    assert env_flag("DEBUG") == expected
    assert bool(env_flag("DEBUG")) == bool(expected)


def test_env_flag_reads_os_environ_live(clean_env):
    clean_env.setenv("HTTPS_DOMAIN", "1")
    assert env_flag("HTTPS_DOMAIN") == 1
    clean_env.setenv("HTTPS_DOMAIN", "0")
    assert env_flag("HTTPS_DOMAIN") == 0


def test_env_flag_falls_back_to_dotenv_loaded_settings(clean_env, monkeypatch):
    clean_env.delenv("TURN_OFF_SINGLE_USER_MODE", raising=False)
    monkeypatch.setattr(
        config, "settings", Settings(_env_file=None, TURN_OFF_SINGLE_USER_MODE="1")
    )
    assert env_flag("TURN_OFF_SINGLE_USER_MODE") == 1


# --- recorded scenario environment (DEBUG + ?domain=<slug>) -------------------


def test_recorded_scenario_env_loads(clean_env):
    # All six recorded scenarios run under DEBUG with DOMAIN_QUERY_PARAM='domain'.
    clean_env.setenv("DEBUG", "1")
    clean_env.setenv("DOMAIN_QUERY_PARAM", "domain")
    clean_env.setenv("ROOT_DOMAIN", "localhost:9222")
    clean_env.setenv("HTTPS_DOMAIN", "0")
    clean_env.setenv("NODE_ENV", "development")
    clean_env.setenv("PORT", "9222")
    s = Settings(_env_file=None)
    assert env_flag("DEBUG") == 1  # if (!!Number(process.env.DEBUG)): taken
    assert s.DOMAIN_QUERY_PARAM == "domain"  # ?domain=<slug> resolution key
    assert env_flag("HTTPS_DOMAIN") == 0  # http:// scheme in the URL builders
    assert env_flag("TURN_OFF_SINGLE_USER_MODE") == 0  # single-user mode active
    assert s.ROOT_DOMAIN == "localhost:9222"


# --- ADR-003: GHOST_API_KEY never in code --------------------------------------


def test_ghost_api_key_has_no_code_default_and_reads_env_only(clean_env):
    assert Settings(_env_file=None).GHOST_API_KEY is None
    assert Settings.model_fields["GHOST_API_KEY"].default is None
    clean_env.setenv("GHOST_API_KEY", "secret-store-value")
    assert Settings(_env_file=None).GHOST_API_KEY == "secret-store-value"


def test_leaked_ghost_api_key_literal_absent_from_repo():
    # Assembled from two fragments so this test file itself never contains it.
    leaked = "3ed1f08bc38fe9e7" + "dfd325bd87"
    offenders = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            if leaked in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))
        except (UnicodeDecodeError, OSError):
            continue
    assert offenders == []


# --- ADR-010: utils/utils.js drop recorded --------------------------------------


def test_utils_dead_code_drop_recorded_in_module_docstring():
    doc = config.__doc__ or ""
    assert "utils/utils.js" in doc
    assert "ADR-010" in doc
    assert "module.exports = {}" in doc


def test_module_surface_is_json_serialisable_config():
    # The settings object exposes exactly the documented env names as fields.
    assert set(Settings.model_fields) == set(CONFIG_ENV_KEYS)
    dumped = json.loads(settings.model_dump_json())
    assert set(dumped) == set(CONFIG_ENV_KEYS)
