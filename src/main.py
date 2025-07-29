from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def welcome():
    return "Welcome to my Rag-app"
