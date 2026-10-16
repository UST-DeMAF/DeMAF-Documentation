# DeMAF Documentation

Documentation of the Deployment Model Abstraction Framework (DeMAF), published at **<https://ust-demaf.github.io/DeMAF-Documentation/>**.

The Markdown sources live in [`docs/`](docs/README.md). Every push to `main` rebuilds and deploys the site via GitHub Actions.

## Local preview

Requires Python 3. Install the dependencies into a virtual environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then start the preview server:

```shell
mkdocs serve
```

The site is then served at <http://127.0.0.1:8000> and reloads on every change. In later sessions, only `source .venv/bin/activate` and `mkdocs serve` are needed.
