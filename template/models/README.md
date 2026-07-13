# Models

What belongs in `models/` and what stays out of git.

## Rules

- Commit only lightweight self-developed or fine-tuned models (~100 MB, case by case)
- Never commit third-party models (Hugging Face etc.) - move them through model sync (S3), even once downloaded here
- Every committed model gets a `<model>.md` sidecar - what it is, how trained, inputs/outputs, metrics

## Layout

Group by purpose - `embedders/`, `classifiers/`, one folder per role. Large or external models move via `make sync_models_up` / `make sync_models_down`, not git.
