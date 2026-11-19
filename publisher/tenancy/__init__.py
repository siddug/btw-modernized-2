"""Target module ``tenancy`` (build order 5).

Source modules: ``app``, ``routes-public``. Depends on: ``config``.

Responsibilities (from the approved system design):

* Domain-slug resolution middleware, run after static and ``/internal`` but
  before the public router: when ``DEBUG`` is truthy the slug comes from
  ``query_params[DOMAIN_QUERY_PARAM]`` (else ``''``); otherwise the hostname
  (``X-Forwarded-Host`` when present, ADR-011) is split at the first dot —
  remainder equal to ``ROOT_DOMAIN`` means subdomain slug with the
  ``publish`` label replaced by the query param, anything else (including a
  dotless bare hostname) is a custom domain with the whole hostname as slug.
* Both branches call ``next()``; the commented-out redirect-to-404 is NOT
  implemented — empty slugs flow into the routers and 404 per-route.
* URL builders ``main_url(request)`` / ``create_sub_url_with_path(request,
  path)`` over ``HTTPS_DOMAIN`` / ``DEBUG`` / ``ROOT_DOMAIN`` /
  ``DOMAIN_QUERY_PARAM`` producing byte-identical strings.
* Exposes the resolved ``(domainSlug, customDomain)`` pair as
  ``request.state.domainSlug`` / ``request.state.customDomain`` (the
  ``res.locals`` equivalent).

This scaffold stub intentionally contains no runtime code yet.
"""
