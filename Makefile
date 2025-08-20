deps:
	poetry install

dist:
	poetry install -q
	poetry build

.git/hooks/%: hooks/run-hook
	@rm -f .git/hooks/%
	@ln -s ../../hooks/run-hook .git/hooks/%
	@chmod u+x .git/hooks/%

.git/hooks/commit-msg: hooks/run-hook
	@rm -f .git/hooks/commit-msg
	@ln -s ../../hooks/run-hook .git/hooks/commit-msg
	@chmod u+x .git/hooks/commit-msg

install-hooks: .git/hooks/commit-msg .git/hooks/pre-commit

dev: install-hooks
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

dev-deps: install-hooks
	@poetry install -q --only dev

lint: dev-deps
	@echo -n "mypy: "
	@poetry run mypy
	@echo -n "flake8: "
	@poetry run flake8
	@echo "pass"
	@echo -n "ruff: "
	@poetry run ruff check

changelog: dev-deps
	poetry run semantic-release --strict --noop version

publish: changelog
	poetry run semantic-release --strict publish

.PHONY: dist dev doc-deps docs docs-apidoc docs-markdown docs-html dev-deps changelog install-hooks lint
