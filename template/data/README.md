# Data

What belongs in `data/` and what stays out of git.

## Rules

- Not committed by default - folder tree and Markdown tracked, data files gitignored
- Only small (~50 MB), processed, non-reproducible data may be committed
- External and large data lives in cloud storage (S3, Azure, GCS); fetch with `make sync_data_down` when configured
- Every data folder keeps a `README.md` index - one line per dataset: provenance + location
- Every large file (dump, parquet) gets a `<file>.md` sidecar - contents, origin, how to regenerate or re-download

## Layout

- `raw/` - original, immutable; never edit in place
- `interim/` - transformed data; processed DB dumps under `interim/dumps/`
- `processed/` - final, canonical datasets for modeling
- `external/` - third-party sources; raw DB dumps under `external/dumps/`
