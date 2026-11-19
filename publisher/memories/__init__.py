"""Target module ``memories`` (build order 3). Source module: ``logic-memories``.

Depends on: ``db``.

Responsibilities (from the approved system design):

* ``get_public_memories(user_id)``: per-request, uncached
  ``SELECT * FROM btw.memories WHERE user_id = $1 AND private = false
  ORDER BY visited_date DESC NULLS LAST, created_at DESC`` — ``private =
  false`` also excludes NULL rows and ``NULLS LAST`` must stay explicit; the
  column list is ``SELECT *`` and must not be narrowed.
* ``photo_urls`` is ``json.loads``-ed only when the column arrives as a
  string; an invalid JSON string raises and the sole caller swallows it into
  ``hasMemories = false``.

This scaffold stub intentionally contains no runtime code yet.
"""
