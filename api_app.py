from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI Agent API is running!"}

@app.get("/get_returns")
def get_returns():
    df = pd.read_excel("data/returns.xlsx")
    return df.to_dict(orient="records")

@app.get("/get_orders")
def get_orders():
    df = pd.read_excel("data/orders.xlsx")
    return df.to_dict(orient="records")
