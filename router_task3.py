"""
Part 3. Multiple Path Parameters
Run with:
    gunicorn "router_task3:app" --bind 127.0.0.1:8000 --workers 1
"""
from router_core import Router

app = Router(name="Router", types_enabled=False)


@app.get("/book/<id>/page/<number>/paragraph/<section>")
def details(id: str, number: str, section: str) -> str:  # noqa: A002
    return f"Book ID: {id}, Page Number: {number}, Paragraph: {section}"