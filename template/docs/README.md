# Documentation

Project documentation - the written record of how the work was done and what was decided.

- Dataset recipe - how the data was sourced, cleaned, and assembled
- Model recipe - architectures, training procedure, hyperparameters
- Exploration and scientific method walkthrough - what was tried and what it showed
- Experiments - designs, runs, and outcomes
- SOTA solution - the current best approach and why it wins
- Acceptance criteria - what the deliverable must satisfy
- Defects - known issues and their status

Material brought in from outside the project belongs in `references/`; generated analysis output
and figures belong in `reports/`.
{% if docs == 'mkdocs' %}
## Generating the docs

Use the [mkdocs](http://www.mkdocs.org/) structure under `docs/` to update the documentation.

Build locally with:

    mkdocs build

Serve locally with:

    mkdocs serve
{% endif %}
