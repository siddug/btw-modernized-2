"""Target module ``db`` (build order 1). Source module: ``services-db``.

Depends on: ``config``.

Responsibilities (from the approved system design):

* Process-wide singleton async PostgreSQL pool for
  ``settings.TASKS_DATABASE_URL`` with max 10 connections, created lazily on
  first use (mirrors ``getTasksDB()``); asyncpg keeps the native ``$1..$n``
  placeholders so every SQL string ports unchanged (ADR-013).
* TLS exactly as source: an SSL context with ``verify_mode=CERT_NONE`` and
  ``check_hostname=False`` only when ``NODE_ENV=production``, otherwise no
  TLS at all.
* Idle-client pool errors are logged (``Unexpected error on idle client``)
  and swallowed, never raised; the source's ``pool.on('error')`` has no 1:1
  asyncpg equivalent, so this is a logging wrapper (ADR-013).
* Read-only access to the ``btw`` schema: ``btw.users``,
  ``btw.custom_domains``, ``btw.notes``, ``btw.memories`` — every recorded
  scenario shows a byte-identical ``pg_dump`` before/after.

This scaffold stub intentionally contains no runtime code yet.
"""
