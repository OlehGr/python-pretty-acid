# Python Pretty ACID

Это небольшой репозиторий для демонстрации реализации вложенных транзакций в Python на базе SQLAlchemy:
 - как сделать базовую вариацию Unit of work без боли
 - как внедрить это в рамках чистой архитектуры
 - как подружить это c DI
 - протестить, что это нечто не оставляет после себя гору "мёртвых" транзакций

## Настройка
```
uv sync
```
```
uv run -m alembic upgrade head
```

Прогнать тесты:
```
uv run -m pytest
```

*Тесты гоняются на реальной БД, в репозитории есть example.env. Если под рукой БД нет, поднять можно командой:
```
docker run -d --name postgres-test -e POSTGRES_DB=testdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
```
