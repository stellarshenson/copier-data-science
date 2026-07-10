# Data

Guidance for what belongs in `data/` and what stays out of the repository.

## What to commit

- **Do not commit data by default** - the directory layout is tracked via `.gitkeep`, contents stay gitignored
- **Small, processed, non-reproducible data may be committed** - up to about 50 MB, and only when it cannot be regenerated cheaply from source
- **Everything else stays external** - raw dumps, large datasets, and anything reproducible from a pipeline or a download

## External data

Most data lives outside the repository - in cloud storage (S3, Azure, GCS) or at a public source. For every external dataset, commit a short Markdown description so the data can be located and re-downloaded later:

- A `README.md` in the relevant `data/` subfolder, or a `<dataset>.md` sidecar placed where the data would live
- Record what the data is, its provenance (origin, license, date), and its exact location (S3 URI, bucket, URL) together with the command needed to fetch it (for example `make sync_data_down` when cloud storage is configured)

## Layout

- `raw/` - original, immutable dumps; never edit in place
- `interim/` - intermediate, transformed data
- `processed/` - final, canonical datasets for modeling
- `external/` - data from third-party sources
