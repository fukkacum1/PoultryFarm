from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import bird, cell, worker


def create_app() -> FastAPI:
    app =  FastAPI(
        title="ебучая птицефабрика"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(bird.router, tags=["Птицы 🐓"])
    app.include_router(cell.router, tags=["Клетки 🪺"])
    app.include_router(worker.router, tags=["Рабы 👷‍♀️"])

    return app


app = create_app()

