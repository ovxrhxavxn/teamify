from fastapi import FastAPI


app = FastAPI(title="Teamify API")


app.get("/")
async def index():
    pass