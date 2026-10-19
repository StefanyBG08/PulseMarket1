from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import or_, asc, desc
from sqlalchemy.exc import IntegrityError
from .extensions import db
from .models import Product, WorkItem
from .validators import validate_product, validate_product_query, validate_product_query, STATUSES

api_bp = Blueprint("api", __name__)

@api_bp.get("/products")
@login_required
def list_products():
    params, error = validate_product_query(request.args)
    if error:
        return jsonify(error=error), 400
    query = Product.query.filter(Product.deleted_at.is_(None))
    if params["q"]:
        like = f"%{params['q']}%"
        query = query.filter(or_(Product.name.ilike(like), Product.sku.ilike(like)))
    if params["category"]:
        query = query.filter(Product.category == params["category"])
    sort_col = getattr(Product, params["sort"])
    query = query.order_by(asc(sort_col) if params["direction"] == "asc" else desc(sort_col))
    started = datetime.now(timezone.utc)
    total = query.order_by(None).count()
    items = query.offset((params["page"] - 1) * params["page_size"]).limit(params["page_size"]).all()
    elapsed_ms = round((datetime.now(timezone.utc) - started).total_seconds() * 1000)
    return jsonify(items=[serialize_product(item) for item in items], total=total, page=params["page"],
        pageSize=params["page_size"], pages=(total + params["page_size"] - 1) // params["page_size"],
        queryMs=elapsed_ms)

@api_bp.post("/products")
@login_required
def create_product():
    data, errors = validate_product(request.get_json(silent=True))
    if errors:
        return jsonify(error=errors), 400
    product = Product(**data)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="SKU ya existe; utiliza uno diferente."), 409
    return jsonify(serialize_product(product)), 201

@api_bp.delete("/products/<int:product_id>")
@login_required
def soft_delete_product(product_id):
    product = Product.query.filter_by(id=product_id, deleted_at=None).first()
    if not product:
        return jsonify(error="Producto no encontrado."), 404
    product.deleted_at = datetime.now(timezone.utc)
    product.status = "DELETED"
    db.session.commit()
    return jsonify(ok=True)

@api_bp.patch("/products/bulk-price")
@login_required
def bulk_update_prices():
    payload = request.get_json(silent=True) or {}
    category = str(payload.get("category", "")).strip()
    try:
        percent = Decimal(str(payload.get("percent", "")))
    except InvalidOperation:
        return jsonify(error="Porcentaje inválido."), 400
    if not category or not percent.is_finite() or percent < -90 or percent > 500:
        return jsonify(error="Categoría requerida y porcentaje entre -90 y 500."), 400
    products = Product.query.filter_by(category=category, deleted_at=None).all()
    try:
        for product in products:
            product.price = (Decimal(product.price) * (Decimal("1") + percent / Decimal("100"))).quantize(Decimal("0.01"))
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="No se pudo completar la actualización masiva."), 500
    return jsonify(updated=len(products))

@api_bp.get("/operations")
@login_required
def list_operations():
    items = WorkItem.query.order_by(WorkItem.updated_at.desc()).limit(100).all()
    return jsonify([{"id": item.id, "title": item.title, "kind": item.kind, "status": item.status,
        "priority": item.priority, "details": item.details} for item in items])

@api_bp.patch("/operations")
@login_required
def update_operation():
    payload = request.get_json(silent=True) or {}
    item_id = payload.get("id")
    status = payload.get("status")
    if not isinstance(item_id, int) or status not in STATUSES:
        return jsonify(error="ID o estado inválido."), 400
    item = db.session.get(WorkItem, item_id)
    if not item:
        return jsonify(error="Tarea no encontrada."), 404
    item.status = status
    item.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(id=item.id, status=item.status)

def serialize_product(product):
    return {"id": product.id, "sku": product.sku, "name": product.name, "category": product.category,
        "price": str(product.price), "stock": product.stock, "status": product.status,
        "createdAt": product.created_at.isoformat() if product.created_at else None}
