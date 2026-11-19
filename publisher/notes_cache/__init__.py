"""Target module ``notes-cache`` (design name ``notes-cache``, build order 2).

Source module: ``logic-notes``. Depends on: ``db``, ``config``.

Responsibilities (from the approved system design):

* Owns the five process-local maps: ``USER_CACHE``, ``USER_ID_SLUG_CACHE``,
  ``CUSTOM_DOMAIN_CACHE``, ``CUSTOM_DOMAIN_ID_SLUG_CACHE``,
  ``NOTE_SLUG_CACHE`` — kept process-local, no Redis (ADR-005).
* ``cache_users({user_id})`` / ``cache_notes({user_id})`` 1000-row paginated
  warmers (``LIMIT 1000 OFFSET n``); full refresh only merges and never
  clears, per-user note refresh replaces that user's map wholesale, no
  locking (last writer wins).
* Cache-first getters ``get_all_notes`` / ``get_note_by_slug`` /
  ``get_user_by_slug`` with SQL fallbacks using the exact source column
  lists, hard 1000-row ceilings, ``published_at DESC`` cache-path sort, and
  the ``ADMIN_SLUG`` single-user rewrite in all three getters.
* Driven by the ``/internal`` refresh endpoints, startup priming and the
  6-hour cron (both scheduled by ``server``).

This scaffold stub intentionally contains no runtime code yet.
"""
