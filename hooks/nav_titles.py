"""Adjust the navigation generated from the folder structure.

- Use the first heading of a section's index page (README.md or index.md) as the section title.
- Order the top-level sections by ORDER; sections not listed follow in alphabetical order.
"""

import re

# Top-level folders in the order they appear in the navigation
ORDER = ["gettingStarted", "architecture", "transformations", "typeDefinitions", "dev"]

HEADING = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.MULTILINE)


def on_nav(nav, config, files):
    _set_titles(nav.items)
    nav.items.sort(key=_position)

    # Update the previous/next page links to the new order
    nav.pages = list(_pages(nav.items))
    for i, page in enumerate(nav.pages):
        page.previous_page = nav.pages[i - 1] if i > 0 else None
        page.next_page = nav.pages[i + 1] if i + 1 < len(nav.pages) else None
    return nav


def _set_titles(items):
    for item in items:
        if not item.is_section:
            continue
        index = next(
            (child for child in item.children if child.is_page and child.file.name in ("index", "README")),
            None,
        )
        if index is not None:
            match = HEADING.search(index.file.content_string)
            if match:
                item.title = match.group(1)
        _set_titles(item.children)


def _position(item):
    if not item.is_section:
        return -1  # Home page and other top-level pages first
    page = next(_pages([item]), None)
    folder = page.file.src_uri.split("/")[0] if page else ""
    return ORDER.index(folder) if folder in ORDER else len(ORDER)


def _pages(items):
    for item in items:
        if item.is_page:
            yield item
        elif item.is_section:
            yield from _pages(item.children)
