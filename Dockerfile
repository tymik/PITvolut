FROM python:3.12.3-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY src/ ./src/

ENTRYPOINT ["python", "-m", "pitvolut"]
