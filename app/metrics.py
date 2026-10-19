from decimal import Decimal
from babel.numbers import format_currency as babel_format_currency

def sum_revenue(sales):
    return sum((Decimal(str(s.total)) for s in sales), Decimal("0.00"))

def average_order_value(revenue, orders):
    return Decimal(str(revenue)) / orders if orders else Decimal("0.00")

def low_stock_count(products, threshold=10):
    return sum(1 for product in products if product.stock < threshold)

def inventory_forecast(stock, daily_demand):
    if daily_demand <= 0:
        return None
    return max(0, int(stock // daily_demand))

def percent_change(current, previous):
    if previous == 0:
        return 0 if current == 0 else 100
    return ((current - previous) / abs(previous)) * 100

def format_currency(value, currency="USD"):
    return babel_format_currency(Decimal(str(value)), currency, locale="es_MX")
