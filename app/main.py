from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.routers import index as core_router
app = FastAPI()

@app.get('/')
def main():
    return JSONResponse(
        content={
            'status':200
        }
    )
app.include_router(core_router.router, prefix="/home")