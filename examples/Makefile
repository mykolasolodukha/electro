ifneq ("$(wildcard .env)","")
include .env
endif


COMMIT_MSG_TEMPLATE = ":bookmark: Release \`v{version}\`"

SOURCES_DIR = "."


.PHONY: env
env:
	poetry install

# TODO: [2024-07-20 by Mykola] Enable style checks.
#.PHONY: style
#style:
#	poetry run black $(SOURCES_DIR)
#	poetry run isort $(SOURCES_DIR)
#	poetry run pylint $(SOURCES_DIR)
#	poetry run pydocstyle $(SOURCES_DIR)

# TODO: [2024-07-20 by Mykola] Enable docs generation.
#.PHONY: docs
#docs:
#	sphinx-apidoc --force --append-syspath --output-dir ./docs/source $(SOURCES_DIR)
#	cd docs && $(MAKE) html

.PHONY: migrate
migrate:
	poetry run aerich upgrade


# region Locales management with Poeditor
# TODO: [2024-07-20 by Mykola] Use `$(SOURCES_DIR)` instead of `.` in the commands below.
.PHONY: extract-locales
extract-locales:
	poetry run pybabel extract --input-dirs . --output ./locales/messages.pot

.PHONY: compile-locales
compile-locales:
	poetry run pybabel compile --directory ./locales/

.PHONY: download-translations
download-translations:
	@./scripts/download_translations_from_poeditor.sh $(POEDITOR__API_TOKEN) $(POEDITOR__PROJECT_ID) $(SOURCES_DIR)

.PHONY: upload-translations
upload-translations:
	@./scripts/upload_translations_to_poeditor.sh $(POEDITOR__API_TOKEN) $(POEDITOR__PROJECT_ID) $(SOURCES_DIR)

.PHONY: upload-locales
upload-locales: extract-locales upload-translations

.PHONY: update-locales
update-locales: download-translations compile-locales

# endregion


# region Versioning
.PHONY: commit_version
commit_version:
	@{ \
		git add pyproject.toml; \
		VERSION=$$(poetry version | cut -d' ' -f2); \
		COMMIT_MSG=$$(echo $(COMMIT_MSG_TEMPLATE) | sed "s/{version}/$${VERSION}/g"); \
		echo "Bumped version: $${VERSION}"; \
		echo "Generated Commit Message: $${COMMIT_MSG}"; \
		git commit -m "$${COMMIT_MSG}" -- pyproject.toml; \
		git tag "v$${VERSION}"; \
	}

.PHONY: bump-major
bump-major:
	poetry version major
	$(MAKE) commit_version

.PHONY: bump-minor
bump-minor:
	poetry version minor
	$(MAKE) commit_version

.PHONY: bump-patch
bump-patch:
	poetry version patch
	$(MAKE) commit_version

# endregion


.PHONY: pre-start
pre-start:
	make migrate
	make update-locales

.PHONY: start
start:
	poetry run python ./test_flow.py