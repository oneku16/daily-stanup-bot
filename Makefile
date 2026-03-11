COMPOSE_DEV = docker-compose -f docker/dev/docker-compose.yml
COMPOSE_PROD = docker-compose -f docker/prod/docker-compose.yml

run-d:
	$(COMPOSE_DEV) up -d --build

run-p:
	$(COMPOSE_PROD) up -d --build

stop-d:
	$(COMPOSE_DEV) down

stop-p:
	$(COMPOSE_PROD) down

migrations:
	uv run alembic revision --autogenerate

migrate:
	uv run alembic upgrade head

test:
	uv run pytest .
