"""
Part 4. [Optional] Type Validation
Run with:
    gunicorn "router_task4_bonus:app" --bind 127.0.0.1:8000 --workers 1
"""
from router_core import Router

# Enable types in core
app = Router(name="Router", types_enabled=True)


@app.get("/book/<id:int>")
def typed_book(id: int) -> str:  # noqa: A002
    return f"Book #{id}"