"""Target module ``public-routes`` (design name ``public-routes``, build order 6).

Source modules: ``routes-public``, ``routes-sitemap``. Depends on:
``config``, ``notes-cache``, ``memories``, ``templates``, ``tenancy``.

Responsibilities (from the approved system design):

* Serves the five public GET operations in declaration order —
  ``/sitemap.xml``, ``/``, ``/about``, ``/memories``, then the catch-all
  ``/{slug}`` — so ``/sitemap.xml`` wins over ``/{slug}``.
* Every handler resolves the user via ``notes-cache.get_user_by_slug``;
  no user -> status 404 rendering ``notfound`` with ``{user: true}``.
* ``GET /`` deep-copies notes before mutation (url, excerpt heuristic,
  readableDate), buckets non-private notes by year, renders ``index.hbs``;
  ``/about`` and ``/memories`` render their views with ``tasksUrl``;
  ``/sitemap.xml`` is an unescaped string-interpolated urlset sent as
  ``application/xml`` (unknown user -> 404 notfound as text/html);
  ``/{slug}`` has NO private filter, extracts meta_image/meta_description,
  renders ``post.hbs``, 404 ``{post: true}`` when missing.
* Handlers keep the source's no-try/catch, no-next(err) shape (ADR-007).

Dead-code drop recorded here (ADR-010): ``routes-sitemap.js``'s
``genSitemap()`` is an empty TODO stub never registered as a route, so it and
the ``xml`` dependency are not ported.

This scaffold stub intentionally contains no runtime code yet.
"""
