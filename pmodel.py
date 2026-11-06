from fastapi import FastAPI
from pydantic import BaseModel

app =FastAPI()

user_details ={}
cnt_id=0
class User(BaseModel):
    name:str
    phone:int
    email:str
@app.post('/create')
def create_user(user:User):
    global cnt_id
    user_details[cnt_id] = user
    response= { 
        "message": "User created successfully",
        "user_id": cnt_id,
        "user": user_details[cnt_id]
    }
    cnt_id+=1
    return response
@app.get('/users')
def all_users():
    return user_details