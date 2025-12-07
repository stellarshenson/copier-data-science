# Template Options

This template provides a number of choices that you can use to customize your project. The defaults work well for many projects, but lots of tooling choices are supported.

See `copier.yml` in the repository root for all available options and their defaults.

## Using a specific version

By default, Copier will use the latest tagged version. To use a specific version or the latest development changes:

```bash
# Use specific tag
copier copy --trust --vcs-ref v1.0.61 gh:stellarshenson/copier-data-science my-project

# Use latest from master
copier copy --trust --vcs-ref master gh:stellarshenson/copier-data-science my-project
```
