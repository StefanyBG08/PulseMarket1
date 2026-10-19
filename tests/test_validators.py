from app.validators import validate_product, validate_product_query

def valid_product():
    return {"sku":"PM-01","name":"Teclado","category":"Electrónica","price":"99.90","stock":2}

def test_product_valid():
    data, errors = validate_product(valid_product())
    assert not errors and data["sku"] == "PM-01"

def test_negative_price_rejected():
    payload = valid_product(); payload["price"] = -2
    data, errors = validate_product(payload)
    assert data is None and "price" in errors

def test_empty_sku_rejected():
    payload = valid_product(); payload["sku"] = ""
    data, errors = validate_product(payload)
    assert data is None and "sku" in errors

def test_page_defaults():
    data, error = validate_product_query({})
    assert not error and data["page_size"] == 20

def test_page_size_limit():
    data, error = validate_product_query({"pageSize":"500"})
    assert data is None and error
