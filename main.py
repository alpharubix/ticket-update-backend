import uvicorn
from routes.upload_excel import router
from fastapi import FastAPI

app = FastAPI()

app.include_router(router)




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000 ,reload=True,
        log_level="debug",      # same effect as --log-level debug
        access_log=True, )
