# Router – Minimal WSGI Router (Decorators, Path Params, Types)

## Quick start

Create and activate a virtual environment, then install runners:

```bash
python -m venv .venv && source .venv/bin/activate
pip install gunicorn waitress flake8 black
```

## Lint/format

```bash
black .
flake8 .
```

## Run parts

- Part 1:

  ```bash
  gunicorn "router_task1:app" --bind 127.0.0.1:8000 --workers 1
  # or
  waitress-serve --listen=127.0.0.1:8000 router_task1:app
  ```

- Part 2:

  ```bash
  gunicorn "router_task2:app" --bind 127.0.0.1:8000 --workers 1
  ```

- Part 3:

  ```bash
  gunicorn "router_task3:app" --bind 127.0.0.1:8000 --workers 1
  ```

- Part 4 (bonus):
  ```bash
  gunicorn "router_task4_bonus:app" --bind 127.0.0.1:8000 --workers 1
  ```

## Example curls

```bash
curl -i http://127.0.0.1:8000/hello
curl -i -X POST http://127.0.0.1:8000/echo

curl -i http://127.0.0.1:8000/book/123
curl -i http://127.0.0.1:8000/user/alice

curl -i http://127.0.0.1:8000/book/3/page/10/paragraph/intro

curl -i http://127.0.0.1:8000/book/42       # bonus types OK
curl -i http://127.0.0.1:8000/book/abc      # bonus types -> 400 Bad Request
```
