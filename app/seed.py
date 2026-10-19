import random
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from .extensions import db
from .models import Customer, Product, Sale, SaleItem, WorkItem

CATEGORIES = ["Electrónica", "Hogar", "Moda", "Deportes", "Belleza", "Libros"]
CITIES = ["Ciudad de México", "Guadalajara", "Monterrey", "Puebla", "Mérida", "Querétaro"]
FIRST = ["Ana", "Luis", "Sofía", "Diego", "Valentina", "Mateo", "Camila", "Santiago", "Lucía", "Emiliano"]
LAST = ["García", "Hernández", "López", "Martínez", "González", "Pérez", "Rodríguez", "Sánchez", "Ramírez", "Torres"]
NAMES = ["Auriculares", "Lámpara", "Playera", "Mochila", "Crema", "Libro", "Smartwatch", "Botella"]
TASKS = ["Preparar pedido", "Revisar inventario", "Validar cupón", "Contactar cliente", "Reponer producto", "Confirmar envío"]

def seed_demo_data():
    # Solo usar en una base de demostración vacía: elimina registros operativos actuales.
    db.session.query(SaleItem).delete()
    db.session.query(Sale).delete()
    db.session.query(WorkItem).delete()
    db.session.query(Product).delete()
    db.session.query(Customer).delete()
    db.session.commit()
    random.seed(41)
    customers = [Customer(name=f"{FIRST[i % len(FIRST)]} {LAST[(i * 7) % len(LAST)]}",
        email=f"cliente{i}@pulsemkt.demo", city=CITIES[i % len(CITIES)]) for i in range(1000)]
    db.session.add_all(customers); db.session.flush()
    products = [Product(sku=f"PM-{i+1:05d}", name=f"{NAMES[i % len(NAMES)]} {i+1}",
        category=CATEGORIES[i % len(CATEGORIES)], price=Decimal(str(49 + ((i * 37) % 1800) + .99)).quantize(Decimal("0.01")),
        stock=(i * 13) % 80, status="ACTIVE") for i in range(1000)]
    db.session.add_all(products); db.session.flush()
    now = datetime.now(timezone.utc)
    sales = []
    for i in range(10000):
        product = products[(i * 23) % len(products)]
        quantity = 1 + (i % 4)
        sales.append(Sale(order_no=f"PM-ORD-{i+1:06d}", customer=customers[(i * 17) % len(customers)],
            total=product.price * quantity, status=["PAID", "PAID", "SHIPPED", "PENDING"][i % 4],
            created_at=now - timedelta(days=i % 365)))
        if len(sales) >= 500:
            db.session.add_all(sales); db.session.flush()
            batch_sales = sales
            for sale in batch_sales:
                idx = int(sale.order_no.split("-")[-1]) - 1
                prod = products[(idx * 23) % len(products)]
                db.session.add(SaleItem(sale=sale, product=prod, quantity=1 + idx % 4, unit_price=prod.price))
            db.session.commit()
            sales = []
    if sales:
        db.session.add_all(sales); db.session.flush()
        for sale in sales:
            idx = int(sale.order_no.split("-")[-1]) - 1
            prod = products[(idx * 23) % len(products)]
            db.session.add(SaleItem(sale=sale, product=prod, quantity=1 + idx % 4, unit_price=prod.price))
        db.session.commit()
    work_items = [WorkItem(title=f"{TASKS[i % len(TASKS)]} #{i+1}", kind=["ORDER", "INVENTORY", "COUPON"][i % 3],
        status=["TODO", "TODO", "IN_PROGRESS", "DONE"][i % 4], priority=["LOW", "MEDIUM", "HIGH"][i % 3],
        details="Elemento de demostración para el flujo de operaciones.") for i in range(30)]
    db.session.add_all(work_items); db.session.commit()
    return {"customers": len(customers), "products": len(products), "sales": 10000, "sale_items": 10000, "work_items": len(work_items)}
