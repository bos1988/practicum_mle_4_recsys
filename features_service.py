import logging

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from core import SimilarItems


logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Service Starting")

    sim_items_store = SimilarItems()

    sim_items_store.load(
        "/home/mle-user/mle_projects/practicum_mle_4_recsys/similar_items.parquet",
        columns=["item_id_1", "item_id_2", "score"],
    )
    app.state.sim_items_store = sim_items_store

    logger.info("Service Ready!")
    
    yield
    # код ниже выполнится только один раз при остановке сервиса
    logger.info("Service Stopping")


# создаём приложение FastAPI
app = FastAPI(title="features", lifespan=lifespan)

@app.post("/similar_items")
async def recommendations(item_id: int, request: Request, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для item_id
    """

    i2i = request.app.state.sim_items_store.get(item_id=item_id, k=k)

    return i2i
