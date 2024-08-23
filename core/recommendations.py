import os
import sys
import pandas as pd

# относительный импорт:
def get_root(n=1):
    if n == 0:
        return os.path.realpath(__file__)
    else:
        return os.path.dirname(get_root(n-1))
sys.path.append(get_root(2))
from core.logger import logger


class Recommendations:

    def __init__(self):

        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }


    def load(self, rec_type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, rec_type: {rec_type}")
        self._recs[rec_type] = pd.read_parquet(path, **kwargs)
        if rec_type == "personal":
            self._recs[rec_type] = self._recs[rec_type].set_index("user_id")
        logger.info(f"Loaded")


    def get(self, user_id: int, k: int=100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error("No recommendations found")
            recs = []

        logger.debug(f"recs: {recs}")
        return recs


    def stats(self):

        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")


if __name__ == "__main__":

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

    print(rec_store.get(user_id=1049126, k=5))
    print(rec_store.get(user_id="default", k=5))
