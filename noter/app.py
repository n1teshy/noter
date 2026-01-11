from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import noter.utils.constants as c
from noter.models.db.meta import BaseModel, engine
from noter.routes.auth import router as auth_router
from noter.routes.folders import router as folders_router
from noter.routes.notes import router as notes_router
from noter.utils.exceptions import AppException


async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(folders_router, prefix="/folders", tags=["folders"])
app.include_router(notes_router, prefix="/notes", tags=["notes"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.exception_handler(RequestValidationError)
async def format_val_errors(req: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=[
            dict(
                field=list(e[c.FA_FLD_LOC])[1:],
                message=e[c.FA_FLD_MSG],
            )
            for e in exc.errors()
        ],
    )


@app.exception_handler(AppException)
async def handle_app_exception(req: Request, exc: AppException):
    if exc.payload is None:
        return Response(status_code=exc.status)
    return JSONResponse(status_code=exc.status, content=exc.payload)
