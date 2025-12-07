# Copier Template

This project uses [Copier](https://copier.readthedocs.io/) for template generation with update support.

## Why Copier?

Copier offers advantages over traditional template engines:

- **Template updates** - `copier update` applies template changes to existing projects
- **Answer tracking** - `.copier-answers.yml` records choices for reproducibility
- **Native conditionals** - `when:` clause for cleaner question flow
- **Migrations** - Version-aware template updates with migration scripts

## Quick Start

```bash
copier copy --trust gh:stellarshenson/copier-data-science my-project
```

The `--trust` flag is required because the template uses Jinja extensions and post-generation tasks.

With pre-filled answers:

```bash
copier copy --trust gh:stellarshenson/copier-data-science -d project_name="My Project" my-project
```

## Updating Projects

One of Copier's key advantages is updating existing projects when the template changes:

```bash
cd my-existing-project
copier update --trust
```

This will:
1. Read `.copier-answers.yml` to recall your original choices
2. Apply template changes while preserving your modifications
3. Show conflicts for manual resolution if needed

## Template Architecture

```
copier-data-science/
├── copier.yml              # Copier configuration and questions
├── template/               # Template files
│   ├── {{ module_name }}/  # Module directory (rendered)
│   ├── Makefile
│   ├── pyproject.toml
│   └── ...
└── scripts/
    └── post_gen.py         # Post-generation cleanup script
```

## Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Project name (auto-derived from directory) | Directory name |
| `repo_name` | Repository name | Derived from project_name |
| `module_name` | Python module name | `lib_<repo_name>` |
| `environment_manager` | uv, conda, virtualenv, or none | uv |
| `dependency_file` | pyproject.toml, requirements.txt, or environment.yml | pyproject.toml |
| `dataset_storage` | Cloud storage: none, s3, azure, gcs | none |
| `docker_support` | Include Dockerfile and targets | No |
| `env_encryption` | Enable .env encryption | Yes |

See `copier.yml` for the complete list of options and their defaults.

## Dataset Storage Variables

Cloud storage options use conditional questions:

| Variable | Shown When | Description |
|----------|------------|-------------|
| `s3_bucket` | `dataset_storage == 's3'` | S3 bucket name |
| `s3_aws_profile` | `dataset_storage == 's3'` | AWS profile for S3 |
| `azure_container` | `dataset_storage == 'azure'` | Azure container name |
| `gcs_bucket` | `dataset_storage == 'gcs'` | GCS bucket name |

## Technical Notes

### Post-Generation Script

The post-generation script (`scripts/post_gen.py`) receives configuration via command-line arguments from `copier.yml`:

```yaml
_tasks:
  - >-
    python3 "{{ _copier_conf.src_path }}/scripts/post_gen.py"
    --testing-framework "{{ testing_framework }}"
    --linting-and-formatting "{{ linting_and_formatting }}"
    # ... all other configuration arguments
```

The script performs cleanup operations:
- Remove files based on `linting_and_formatting` choice (e.g., `setup.cfg` for ruff)
- Move selected testing framework files to `tests/`
- Move selected docs framework files to `docs/`
- Remove unused dependency files based on `dependency_file` choice
- Write Python version to `pyproject.toml`
- Apply custom config overlay if provided

### Template Suffix

The `_templates_suffix: ""` setting processes all files as Jinja templates. This means `.jinja` extensions are not stripped automatically - the post-gen script handles renaming `.copier-answers.yml.jinja` to `.copier-answers.yml`.

### Answers File

The `.copier-answers.yml` file is generated from a template (`template/.copier-answers.yml.jinja`) that uses the special `_copier_answers` variable:

```yaml+jinja
# Changes here will be overwritten by Copier; NEVER EDIT MANUALLY
{{ _copier_answers|to_nice_yaml -}}
```

This file enables `copier update` to recall user choices when updating projects to newer template versions.

### Jinja Extensions

The template uses `jinja2_time.TimeExtension` for the `{% now %}` tag in LICENSE files.
