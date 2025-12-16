# Multi-language Open-source License Excavator
### or: the `license-mole` that digs up your dependencies

## Installation

Clone this repository and simply run `make` or `poetry install`.

## Usage

Once installed, use `poetry run mole` to invoke Mole.

### Command-line arguments:
```
usage: license-mole [-h] [--version] [--render-only] [--force-scan] [--check] [--output OUTPUT] [ROOT]

Multi-language Open-source License Excavator

positional arguments:
  ROOT                 Path to project root containing mole.toml (default: working directory))

options:
  -h, --help           show this help message and exit
  --version, -v        Show current version of license-mole
  --render-only        Do not scan, render from cached data only
  --force-scan, -f     Scan all dependencies, even if cache is up-to-date
  --check, -c          Quickly verify cached data against package lock files
  --output, -o OUTPUT  Output a specific document, may be specified multiple times (default: all documents)
```

## Development

* ([Development API Documentation](docs/index.md))

Mole uses mypy for type checking and currently uses both Ruff and flake8 for linting. (Ruff's reStructuredText
support is still in preview.)

To install the development dependencies, use `make dev` or `poetry install --all-groups`.

To generate the documentation files:

* `make docs-markdown`: Generate the Markdown documentation found in `docs/`
* `make docs-html`: Generate HTML documentation into `docs/html/`
* `make docs`: Generate both Markdown and HTML documentation

## License

Copyright &copy; 2025 Posit Software, PBC

Mole is distributed under the MIT license. See the [LICENSE](LICENSE) file.

Mole wouldn't be successful on its own. See its [open-source dependencies](docs/NOTICE.md).
