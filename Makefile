deps:
	poetry install

dist:
	poetry install -q
	poetry build

dev:
	poetry install --all-groups

doc-deps:
	poetry install -q --with docs

docs: docs-markdown docs-html

docs-apidoc:
	poetry run sphinx-apidoc -o docs/source -e -M -f src/license_mole -t docs/source/templates

docs-markdown: docs-apidoc
	poetry run sphinx-build -b markdown -d docs/.doctrees docs/source docs

docs-html: docs-apidoc
	poetry run sphinx-build -b html -d docs/.doctrees docs/source docs/html

.PHONY: build docs docs-apidoc docs-markdown docs-html
