"""Target module ``internal-routes`` (design name ``internal-routes``, build order 7).

Source module: ``routes-internal``. Depends on: ``notes-cache``.

Responsibilities (from the approved system design):

* ``POST /internal/cache/refresh/user`` and ``POST /internal/cache/refresh/notes``,
  mounted at ``/internal`` before the tenancy middleware, so these requests
  never receive domain state; no authentication of any kind (ADR-006 —
  exposure decision stays a proposed ADR for G3).
* Always HTTP 200 with a JSON envelope: ``{"success": true}`` on success;
  ``{"success": false, "error": "Invalid or empty input"}`` when ``user_id``
  is missing from the optional JSON or x-www-form-urlencoded body;
  ``{"success": false, "error": str(e)}`` when a warmer throws (DB error text
  leaks into the 200 body).
* Only per-user refreshes are reachable here; the full refresh is driven by
  server startup and the cron only. Concurrent refreshes interleave the
  shared maps with no locking.

This scaffold stub intentionally contains no runtime code yet.
"""
