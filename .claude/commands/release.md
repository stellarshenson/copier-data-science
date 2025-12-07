# Release Command

Release a new version of the copier-data-science template.

## Instructions

1. Read `pyproject.toml` and find the current version (e.g., `version = "1.0.61"`)
2. Increment the patch version by 1 (e.g., `1.0.61` -> `1.0.62`)
3. Update `pyproject.toml` with the new version
4. Commit the version change with message: `chore: bump version to <new_version>`
5. Create new tag `v<new_version>`
6. Push commit and tag to origin

**IMPORTANT**: Do NOT delete old tags - they are needed for `copier update` to work on existing projects.
