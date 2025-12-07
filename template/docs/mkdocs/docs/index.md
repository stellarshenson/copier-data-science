# {{ project_name }} documentation!
{% if project_description is not none %}
## Description

{{ description }}
{% endif %}
## Commands

The Makefile contains the central entry points for common tasks related to this project.
{% if dataset_storage != 'none' %}
### Syncing data to cloud storage

{% if dataset_storage.s3 -%}
* `make sync_data_up` will use `aws s3 sync` to recursively sync files in `data/` up to `s3://{{ s3_bucket }}/data/`.
* `make sync_data_down` will use `aws s3 sync` to recursively sync files from `s3://{{ s3_bucket }}/data/` to `data/`.
{% elif dataset_storage.azure -%}
* `make sync_data_up` will use `az storage blob upload-batch -d` to recursively sync files in `data/` up to `{{ azure_container }}/data/`.
* `make sync_data_down` will use `az storage blob upload-batch -d` to recursively sync files from `{{ azure_container }}/data/` to `data/`.
{% elif dataset_storage.gcs -%}
* `make sync_data_up` will use `gsutil rsync` to recursively sync files in `data/` up to `gs://{{ gcs_bucket }}/data/`.
* `make sync_data_down` will use `gsutil rsync` to recursively sync files in `gs://{{ gcs_bucket }}/data/` to `data/`.
{% endif %}
{% endif %}
