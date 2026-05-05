# python:3.13.12-slim-bookworm
FROM python@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

# Install uv
# ghcr.io/astral-sh/uv:0.11.3
COPY --from=ghcr.io/astral-sh/uv@sha256:90bbb3c16635e9627f49eec6539f956d70746c409209041800a0280b93152823 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project

COPY . .

CMD ["uv", "run", "python", "main.py"]

