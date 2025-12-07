# Contributing

The Copier Data Science project is opinionated, but not afraid to be wrong. Best practices change, tools evolve, and lessons are learned. **The goal of this project is to make it easier to start, structure, and share an analysis.** [Pull requests](https://github.com/stellarshenson/copier-data-science/pulls) and [filing issues](https://github.com/stellarshenson/copier-data-science/issues) is encouraged. We'd love to hear what works for you, and what doesn't.

## Running the tests

```bash
pip install -r dev-requirements.txt
pytest tests -v
```

Fast mode for quick iteration:

```bash
pytest tests -F   # Single config
pytest tests -FF  # Skip Makefile validation
pytest tests -FFF # Both
```
