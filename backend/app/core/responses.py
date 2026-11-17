from typing import Any


def ok(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"data": data, "meta": meta or {}}


def paginated(data: Any, page: int, limit: int, total: int) -> dict[str, Any]:
    pages = (total + limit - 1) // limit if total else 0
    return ok(data, {"page": page, "limit": limit, "total": total, "pages": pages})
