from decimal import Decimal
from app.metrics import sum_revenue, average_order_value, low_stock_count, inventory_forecast, percent_change, format_currency

def test_sum_revenue():
    class Sale: 
        def __init__(self, total): self.total = total
    assert sum_revenue([Sale("10.00"), Sale("15.50")]) == Decimal("25.50")

def test_average_order_value():
    assert average_order_value(120, 3) == 40

def test_average_zero_orders():
    assert average_order_value(120, 0) == Decimal("0.00")

def test_low_stock_count():
    class Product:
        def __init__(self, stock): self.stock = stock
    assert low_stock_count([Product(2), Product(10), Product(0)]) == 2

def test_low_stock_custom_threshold():
    class Product:
        def __init__(self, stock): self.stock = stock
    assert low_stock_count([Product(4), Product(6)], 5) == 1

def test_inventory_forecast():
    assert inventory_forecast(21, 4) == 5

def test_inventory_forecast_zero_demand():
    assert inventory_forecast(30, 0) is None

def test_inventory_forecast_never_negative():
    assert inventory_forecast(0, 3) == 0

def test_percent_change_positive():
    assert percent_change(120, 100) == 20

def test_percent_change_negative():
    assert percent_change(75, 100) == -25

def test_percent_change_zero_base():
    assert percent_change(5, 0) == 100

def test_currency_format():
    assert "100" in format_currency(100, "USD")
