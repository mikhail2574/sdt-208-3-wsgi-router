"""
Part 2. Path Parameters
Run with:
    gunicorn "router_task2:app" --bind 127.0.0.1:8000 --workers 1
"""
from router_core import Router

app = Router(name="Router", types_enabled=False)


@app.get("/book/<id>")
def get_book(id: str) -> str:  # noqa: A002 - parameter name is part of spec
    return f"Book ID is {id}"


@app.get("/user/<username>")
def get_user(username: str) -> str:
    return f"Welcome, {username}"