FROM python:3.12-slim

WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv sync --no-dev
COPY . .
RUN chmod +x docker/entrypoint.sh
ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["uv", "run", "python", "main.py"]
