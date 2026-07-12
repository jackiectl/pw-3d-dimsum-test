"""
Loads content/content.json — the single place every word in the 3D shop is written.

Every make-*.py generator imports CONTENT from here rather than holding its own
strings, so changing a project description or a heading is a text edit plus
`npm run textures`, not a code change.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = json.loads((ROOT / 'content' / 'content.json').read_text(encoding='utf-8'))
