from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from .extensions import db
from .models import Sale, Product, Customer, WorkItem
from .metrics import format_currency, average_order_value

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return render_template("index.html")

@main_bp.get("/dashboard")
@login_required
def dashboard():
    revenue, sale_count = db.session.query(func.coalesce(func.sum(Sale.total), 0), func.count(Sale.id)).one()
    product_count = Product.query.filter_by(status="ACTIVE", deleted_at=None).count()
    customer_count = Customer.query.count()
    pending_count = WorkItem.query.filter(WorkItem.status != "DONE").count()
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(8).all()
    low_stock = Product.query.filter(Product.deleted_at.is_(None), Product.stock < 10).order_by(Product.stock.asc()).limit(6).all()
    return render_template("dashboard.html", revenue=format_currency(revenue), sale_count=sale_count,
        product_count=product_count, customer_count=customer_count, pending_count=pending_count,
        recent_sales=recent_sales, low_stock=low_stock,
        average=format_currency(average_order_value(revenue, sale_count)))


@main_bp.get("/dashboard/products")
@login_required
def products_page():
    from .validators import CATEGORIES
    return render_template("products.html", categories=sorted(CATEGORIES))

@main_bp.get("/dashboard/operations")
@login_required
def operations_page():
    return render_template("operations.html")
