# Models

Guidance for what belongs in `models/` and what stays out of the repository.

## What to commit

- **Commit only lightweight models we developed or fine-tuned** - typically up to about 100 MB, decided case by case
- **Never commit standard third-party models** - anything downloaded from Hugging Face or a similar source must be kept out of git, even once it sits in this folder; move it through the model sync mechanism (S3 upload/download) instead
- **Every committed model needs a sidecar** - a brief `<model>.md` next to it describing what it is, how it was trained or fine-tuned, its inputs and outputs, and any headline metrics

## Layout

Group models into purpose-named subfolders, one per role, for example:

- `embedders/` - embedding models
- `classifiers/` - classification models
- `<purpose>/` - one folder per model role

Large or external models are moved through the model sync mechanism (`make sync_models_up` / `make sync_models_down` when cloud storage is configured), not stored in git.
