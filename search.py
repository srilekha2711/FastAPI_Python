from fastapi import FastAPI
from typing import Optional

app= FastAPI()

products =[
    {"id": 1, "name": "Pen", "category": "Stationery", "price": 30},
    {"id": 2, "name": "Notebook", "category": "Stationery", "price": 120},
    {"id": 3, "name": "T-shirt", "category": "Clothing", "price": 250},
    {"id": 4, "name": "Eraser", "category": "Stationery", "price": 10},
    {"id": 5, "name": "Keyboard", "category": "Electronics", "price": 400}
]
@app.get("/products")
def search_products(category: Optional[str] =None, max_price: Optional[int]=None):
    filtered_products = products
    if category:
        filtered_products = [product for product in filtered_products if product["category"].lower() == category.lower()]
    if max_price:
        filtered_products = [product for product in filtered_products if product["price"] <= max_price]
    return filtered_products