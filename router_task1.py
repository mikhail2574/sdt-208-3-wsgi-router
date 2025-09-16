"""
Part 1. Basic Router with Decorators
Run with:
    gunicorn "router_task1:app" --bind 127.0.0.1:8000 --workers 1
or:
    waitress-serve --listen=127.0.0.1:8000 router_task1:app
"""
from router_core import Router

app = Router(name="Router", types_enabled=False)


@app.get("/hello")
def hello() -> str:
    return "Hello, world!"


@app.post("/echo")
def echo() -> str:
    return "Post received"