import logging
import requests

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from core import Recommendations


logger = logging.getLogger("uvicorn.error")
features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Service Starting")
    
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

    logger.info("Service Ready!")

    yield
    # этот код выполнится только один раз при остановке сервиса
    rec_store.stats()
    logger.info("Service Stopping")


# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, request: Request, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs = request.app.state.rec_store.get(user_id=user_id, k=k)

    return {"recs": recs}

@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]
    logger.debug(f"3 events: {events}")

    # получаем список похожих объектов
    if len(events) > 0:
        item_id = events[0]
        params = {"item_id": item_id, "k": k}
        resp = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        recs = item_similar_items["item_id_2"]
    else:
        recs = []

    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    items = []
    scores = []
    for item_id in events:
        # для каждого item_id получаем список похожих в item_similar_items
        params = {"item_id": item_id, "k": k}
        resp = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        items += item_similar_items["item_id_2"]
        scores += item_similar_items["score"]
    # сортируем похожие объекты по scores в убывающем порядке
    # для старта это приемлемый подход
    combined = list(zip(items, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [item for item, _ in combined]

    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = dedup_ids(combined)

    return {"recs": recs[:k]} 

@app.post("/recommendations")
async def recommendations(user_id: int, request: Request, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, request, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    # добавляем оставшиеся элементы в конец
    recs_blended += recs_online[min_length:]
    recs_blended += recs_offline[min_length:]

    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)
    
    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]

    return {"recs": recs_blended}
