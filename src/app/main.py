import time

from fastapi import Request

from .api import router
from .core.config import settings
from .core.setup import create_application

app = create_application(router=router, settings=settings)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """ Add process time for each API request """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

