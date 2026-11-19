"""publisher — FastAPI port of the Express 4 'publisher' service.

Translation pair: ``node-express__python-fastapi``.

This package is the empty target scaffold produced from the approved design
(``system_design.json``). It contains the nine target module packages in the
design's linear build order 0-8 — see ``publisher/module_graph.json`` — and
intentionally no migrated business behaviour yet: every subpackage
``__init__.py`` is a documentation-only stub. Runtime code lands
module-by-module in build order; a module may only import modules with a
strictly smaller ``build_order``.
"""

__all__ = [
    "config",
    "db",
    "notes_cache",
    "memories",
    "templates",
    "tenancy",
    "public_routes",
    "internal_routes",
    "server",
]
