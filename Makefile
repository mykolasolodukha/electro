COMMIT_MSG_TEMPLATE = ":bookmark: Release \`v{version}\`"

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