from core.db.base_class import Base
from core.db.init_data import init_db
from core.db.exception import ApiHTTPException
from core.db.session import engine
from api.endpoints import books
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title='Library API')
app.include_router(books.router)

@app.exception_handler(ApiHTTPException)
async def api_http_exception_handler(request: Request, exc: ApiHTTPException):
    content={"code": exc.code, "error": exc.error}
    response = JSONResponse(
        status_code=exc.code,
        content = content
    )
    return response

@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    init_db()