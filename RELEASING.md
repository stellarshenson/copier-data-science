# Releasing copier-data-science

## Version Scheme

This project uses semantic versioning: `1.0.PATCH` where PATCH is incremented for each release.

## Release Process

1. **Increment version**
   ```bash
   make increment_version
   ```

2. **Update CHANGELOG.md** with release notes

3. **Commit and tag**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: bump version to $(grep -oP 'version = "\K[^"]+' pyproject.toml)"
   git tag v$(grep -oP 'version = "\K[^"]+' pyproject.toml)
   ```

4. **Push**
   ```bash
   git push origin master --tags
   ```

## Important Notes

- **Do NOT delete old tags** - they are required for `copier update` to work on existing projects
- Tags must have `v` prefix (e.g., `v1.0.62`)
- Copier uses tags to determine template versions for updates
