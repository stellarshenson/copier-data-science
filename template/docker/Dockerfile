# Dockerfile for {{ project_name }}
# Build: make docker_build
# Push: make docker_push
# Override Python version: docker build --build-arg PYTHON_VERSION=3.11 ...

ARG PYTHON_VERSION={{ python_version_number }}
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

{%- if docker_package_manager == 'uv' %}
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy and install the wheel (built by make build)
COPY dist/*.whl /tmp/
RUN uv pip install --system --no-cache /tmp/*.whl && rm -rf /tmp/*.whl
{%- else %}
# Copy and install the wheel (built by make build)
COPY dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
{%- endif %}

# Copy entrypoint
COPY docker/entrypoint.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "entrypoint.py"]
