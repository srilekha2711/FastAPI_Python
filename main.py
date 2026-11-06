from fastapi import FastAPI,HTTPException

app =FastAPI()
@app.get("/")
def home():
    return {"message" : "Hello, World!"}

users ={
    1:{ "name": "Srilekha",
        "orders": {
            101:{"item": "Laptop","amount": 5000},
            102:{"item": "Mouse","amount": 5000}
        }},
    2:{"name": "Sravani",
       "orders": {
                   201:{"item": "Phone","amount": 5000},
                   202:{"item": "Charger","amount": 5000}
               }}
}
@app.get('/user/{user_id}/order/{order_id}')
def get_user(user_id: int, order_id:int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Product Id not found")
    return users[user_id]['orders'][order_id]