import re
from decimal import Decimal, InvalidOperation

CATEGORIES = {"Electrónica", "Hogar", "Moda", "Deportes", "Belleza", "Libros"}
STATUSES = {"TODO", "IN_PROGRESS", "DONE"}

def validate_product(payload):
    errors = {}
    if not isinstance(payload, dict):
        return None, {"body": "Se esperaba un objeto JSON."}
    sku = str(payload.get("sku", "")).strip()
    name = str(payload.get("name", "")).strip()
    category = str(payload.get("category", "")).strip()
    try:
        price = Decimal(str(payload.get("price", "")))
        if not price.is_finite() or price <= 0 or price > Decimal("10000000"):
            errors["price"] = "El precio debe ser positivo y menor a 10,000,000."
    except (InvalidOperation, ValueError):
        price = None
        errors["price"] = "Precio inválido."
    try:
        stock = int(payload.get("stock", ""))
        if stock < 0 or stock > 10000000:
            errors["stock"] = "Stock fuera del rango permitido."
    except (ValueError, TypeError):
        stock = None
        errors["stock"] = "Stock debe ser un entero."
    if not 2 <= len(sku) <= 40:
        errors["sku"] = "SKU debe tener entre 2 y 40 caracteres."
    if not 2 <= len(name) <= 120:
        errors["name"] = "Nombre debe tener entre 2 y 120 caracteres."
    if not 2 <= len(category) <= 80:
        errors["category"] = "Categoría debe tener entre 2 y 80 caracteres."
    if errors:
        return None, errors
    return {"sku": sku, "name": name, "category": category, "price": price, "stock": stock}, {}

def validate_product_query(args):
    try:
        page = int(args.get("page", 1)); page_size = int(args.get("pageSize", 20))
    except (ValueError, TypeError):
        return None, "La página y el tamaño deben ser enteros."
    if page < 1 or not 1 <= page_size <= 100:
        return None, "Página debe ser positiva y pageSize estar entre 1 y 100."
    sort = args.get("sort", "created_at")
    if sort not in {"name", "price", "stock", "created_at"}:
        return None, "Campo de ordenamiento inválido."
    direction = args.get("direction", "desc").lower()
    if direction not in {"asc", "desc"}:
        return None, "Dirección inválida."
    return {"page": page, "page_size": page_size, "q": args.get("q", "").strip()[:120],
            "category": args.get("category", "").strip()[:80], "sort": sort, "direction": direction}, None
