"""Rewrite links between the documentation and included repositories.

- Links to an included repository on GitHub are replaced by links to its page on the site,
  as long as the linked file is published (e.g. the repository's README).
- Relative links in pages of an included repository that point to files not published on
  the site (e.g. source files or folders) are replaced by links to the file on GitHub.
"""

import posixpath
import re

# Docs folder of each included repository and its GitHub URL
REPOSITORIES = {
    "typeDefinitions/": "https://github.com/UST-DeMAF/demaf-type-definitions",
}
BRANCH = "main"

LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(\s*(<[^>]*>|[^)\s]+)([^)]*)\)")
GITHUB_PATH = re.compile(rf"^/(?:tree|blob)/{re.escape(BRANCH)}/(.*)$")


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri
    included = next((folder for folder in REPOSITORIES if src.startswith(folder)), None)

    def published(path):
        return files.get_file_from_path(path) is not None

    def to_site(url):
        """Return the published file a GitHub URL of an included repository points to."""
        for folder, repo_url in REPOSITORIES.items():
            if url.rstrip("/") == repo_url:
                path = ""
            elif url.startswith(repo_url + "/"):
                match = GITHUB_PATH.match(url[len(repo_url):])
                if not match:
                    return None
                path = match.group(1).rstrip("/")
            else:
                continue
            for candidate in (path, posixpath.join(path, "README.md"), posixpath.join(path, "index.md")):
                candidate = posixpath.normpath(folder + candidate)
                if published(candidate):
                    return candidate
        return None

    def rewrite(match):
        text, target, rest = match.groups()
        url = target[1:-1] if target.startswith("<") else target
        url, _, anchor = url.partition("#")
        anchor = f"#{anchor}" if anchor else ""

        if url.startswith("https://github.com/"):
            target_file = to_site(url)
            if target_file is None:
                return match.group(0)
            relative = posixpath.relpath(target_file, posixpath.dirname(src) or ".")
            return f"[{text}](<{relative}{anchor}>{rest})"

        if included is None or not url or re.match(r"^[a-z][a-z0-9+.-]*:|^/", url, re.IGNORECASE):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src), url))
        if published(resolved) or not resolved.startswith(included):
            return match.group(0)
        github_url = f"{REPOSITORIES[included]}/tree/{BRANCH}/{resolved[len(included):]}"
        return f"[{text}](<{github_url}{anchor}>{rest})"

    return LINK.sub(rewrite, markdown)
