FROM python:3.14-slim

# uv берём из официального образа (только бинарники)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 1) Зависимости отдельным слоем: пересобираются только при изменении pyproject/uv.lock.
#    --no-install-project — проект не пакет, ставим только зависимости из lock-файла.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Код приложения
COPY . .

# loguru не создаёт родительские папки для логов
RUN mkdir -p /app/logs && chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
