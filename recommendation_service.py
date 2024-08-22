import logging

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from core import Recommendations


logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")
    
    rec_store = Recommendations()
    
    rec_store.load(
        "personal",
        "/home/mle-user/mle_projects/practicum_mle_4_recsys/final_recommendations_feat.parquet",
        columns=["user_id", "item_id", "rank"],
    )
    rec_store.load(
        "default",
        "/home/mle-user/mle_projects/practicum_mle_4_recsys/top_recs.parquet",
        columns=["item_id", "rank"],
    )
    app.state.rec_store = rec_store

    yield
    # этот код выполнится только один раз при остановке сервиса
    rec_store.stats()
    logger.info("Stopping")


# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations")
async def recommendations(user_id: int, request: Request, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs = request.app.state.rec_store.get(user_id=user_id, k=k)

    return {"recs": recs}
