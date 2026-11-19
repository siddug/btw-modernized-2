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

Dead-code drops recorded here (ADR-010):

* ``utils/utils.js`` exported an empty object and had zero require sites; it
  carries no runtime behaviour and is intentionally not ported.

This scaffold stub intentionally contains no runtime code yet.
"""
