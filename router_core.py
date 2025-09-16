"""
WSGI Router - a tiny WSGI router with decorator-based route registration.
PEP8-compliant, tested with black/flake8 configurations in pyproject.toml.

Features:
- @app.get("/path") and @app.post("/path")
- Static routes and dynamic path parameters: "<name>" or "<name:type>"
- Multiple parameters per route (arbitrary positions)
- Optional basic type casting (str, int)
- Plain-text responses
- Minimal WSGI interface

Usage example (gunicorn):
    gunicorn "router_task1:app" --bind 127.0.0.1:8000 --workers 1

Or with waitress:
    waitress-serve --listen=127.0.0.1:8000 router_task1:app
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

Handler = Callable[..., str]


@dataclass(frozen=True)
class CompiledSegment:
    """Represents a compiled path segment: literal or parameter with type."""

    is_param: bool
    name: Optional[str] = None
    typ: Optional[type] = None
    literal: Optional[str] = None


@dataclass
class Route:
    """Internal route record."""

    method: str
    raw_path: str
    segments: List[CompiledSegment]
    handler: Handler
    types_enabled: bool


class Router:
    """
    A minimal decorator-driven WSGI router.
    Implements __call__(environ, start_response).
    """

    SUPPORTED_TYPES: Dict[str, type] = {"str": str, "int": int}

    def __init__(self, name: str = "Router", types_enabled: bool = True) -> None:
        self.name = name
        self._routes: List[Route] = []
        self._types_enabled = types_enabled

    # -------------------------- Public API (Decorators) --------------------------
    def get(self, path: str) -> Callable[[Handler], Handler]:
        return self._register("GET", path)

    def post(self, path: str) -> Callable[[Handler], Handler]:
        return self._register("POST", path)

    # ------------------------------- WSGI Entry ---------------------------------
    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/") or "/"

        for route in self._routes:
            if route.method != method:
                continue

            matched, params_or_error = self._match_route(route, path)
            if matched:
                try:
                    body = route.handler(**params_or_error)
                    if not isinstance(body, str):
                        body = str(body)
                    response = body.encode("utf-8")
                    start_response(
                        "200 OK",
                        [
                            ("Content-Type", "text/plain; charset=utf-8"),
                            ("Content-Length", str(len(response))),
                        ],
                    )
                    return [response]
                except ValueError as exc:
                    # Type conversion error or similar
                    error_bytes = f"400 Bad Request: {exc}".encode("utf-8")
                    start_response(
                        "400 Bad Request",
                        [
                            ("Content-Type", "text/plain; charset=utf-8"),
                            ("Content-Length", str(len(error_bytes))),
                        ],
                    )
                    return [error_bytes]

        # No route matched
        msg = f"{self.name}: 404 Not Found ({method} {path})"
        data = msg.encode("utf-8")
        start_response(
            "404 Not Found",
            [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(data)))],
        )
        return [data]

    # ------------------------------ Registration -------------------------------
    def _register(self, method: str, path: str) -> Callable[[Handler], Handler]:
        segments = self._compile_path(path)

        def decorator(func: Handler) -> Handler:
            route = Route(
                method=method,
                raw_path=path,
                segments=segments,
                handler=func,
                types_enabled=self._types_enabled,
            )
            self._routes.append(route)
            return func

        return decorator

    # ------------------------------ Path Parsing --------------------------------
    def _compile_path(self, path: str) -> List[CompiledSegment]:
        if not path.startswith("/"):
            raise ValueError(f"Route must start with '/': {path}")

        parts = [s for s in path.split("/") if s != ""]  # drop empty splits
        compiled: List[CompiledSegment] = []

        for part in parts:
            if part.startswith("<") and part.endswith(">"):
                inner = part[1:-1].strip()
                # Handle <name> or <name:type>
                if ":" in inner:
                    name, typ_name = [p.strip() for p in inner.split(":", 1)]
                    py_type = self.SUPPORTED_TYPES.get(typ_name)
                    if py_type is None:
                        raise ValueError(f"Unsupported type '{typ_name}' in segment '{part}'")
                    compiled.append(CompiledSegment(is_param=True, name=name, typ=py_type))
                else:
                    compiled.append(CompiledSegment(is_param=True, name=inner, typ=str))
            else:
                compiled.append(CompiledSegment(is_param=False, literal=part))

        return compiled

    # ------------------------------ Matching Logic ------------------------------
    def _match_route(self, route: Route, path: str) -> Tuple[bool, Dict[str, Any] | str]:
        parts = [s for s in path.split("/") if s != ""]
        if len(parts) != len(route.segments):
            return False, "Segment count mismatch"

        params: Dict[str, Any] = {}

        for part, seg in zip(parts, route.segments):
            if not seg.is_param:
                if part != seg.literal:
                    return False, f"Literal mismatch '{part}' != '{seg.literal}'"
                continue

            # Parameter segment
            value_str = part
            if route.types_enabled and seg.typ and seg.typ is not str:
                try:
                    casted: Any = seg.typ(value_str)
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(
                        f"Failed to convert '{value_str}' to {seg.typ.__name__}"
                    ) from exc
                params[seg.name] = casted
            else:
                params[seg.name] = value_str

        return True, params