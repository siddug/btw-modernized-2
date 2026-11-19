"""Target module ``templates`` (build order 4). Source module: ``app``.

Depends on: ``config``.

Responsibilities (from the approved system design):

* Handlebars-compatible rendering engine (pybars3 per ADR-001) configured
  like express-handlebars: extname ``.hbs``, default layout ``base``,
  ``views/layouts`` and ``views/partials`` directories, a re-implemented
  handlebars-layout block/content mechanism, library helpers ``not``/``and``/
  ``or``, and the four custom helpers with their exact sharp edges
  (``slicer``, ``ifDev``, ``ifIsNthItem``, ``dateddmmyyy``).
* The seven views (index, about, memories, post, notfound, layouts/base,
  partials/sidebar) port as-is; rendered bodies are byte-compared by the
  recorded scenarios.
* Prod-only HTML minification with the exact seven-option htmlMinifier set,
  gated on ``NODE_ENV === 'production'`` (ADR-002).
* Static serving of ``public/`` mounted before all routers so static files
  win over routes.

This scaffold stub intentionally contains no runtime code yet.
"""
