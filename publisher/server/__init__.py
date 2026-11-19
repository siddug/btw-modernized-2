"""Target module ``server`` (build order 8). Source modules: ``app``, ``server-entry``.

Depends on: ``config``, ``notes-cache``, ``templates``, ``tenancy``,
``public-routes``, ``internal-routes``.

Responsibilities (from the approved system design):

* Assembles the FastAPI application preserving the source middleware/mount
  order (ADR-014): prod-only HTML minify -> morgan 'dev' request logging
  (ADR-012) -> JSON and urlencoded body parsing -> cookie parsing ->
  ``StaticFiles(public/)`` -> ``/internal`` sub-application -> tenancy
  domain-slug middleware -> public router at ``/``.
* Lifespan startup primes the caches once (``cache_users()`` /
  ``cache_notes()``) before the first request and schedules the 6-hourly
  cron ``0 */6 * * *`` re-prime (ADR-008).
* Exception handler kept as the source equivalent: status
  ``getattr(err, 'status', None) or 500`` with an empty body, never a render
  (ADR-007).
* Entrypoint (absorbs ``bin/www``): uvicorn on host ``0.0.0.0`` with
  ``PORT`` default ``9222``; ``EACCES``/``EADDRINUSE`` -> log to stderr and
  ``sys.exit(1)`` (pm2 contract), any other error re-raised; readiness
  logged as ``Listening on port <bind>`` on the ``pythagoras:server``
  logger (ADR-009). Exports the configured app object (the
  ``module.exports = app`` equivalent).

This scaffold stub intentionally contains no runtime code yet.
"""
