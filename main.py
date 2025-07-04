import uvicorn
from routes.upload_excel import router
from fastapi import FastAPI

app = FastAPI()

app.include_router(router)


