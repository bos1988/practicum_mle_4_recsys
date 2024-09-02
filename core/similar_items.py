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


class SimilarItems:

    def __init__(self):

        self._similar_items = None

    def load(self, path, **kwargs):
        """
        Загружаем данные из файла
        """

        logger.info(f"Loading data")
        self._similar_items = pd.read_parquet(path, **kwargs)
        self._similar_items = self._similar_items.set_index("item_id_1")
        logger.info(f"Loaded")

    def get(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items.loc[item_id].head(k)
            i2i = i2i[["item_id_2", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"item_id_2": [], "score": {}}

        return i2i


if __name__ == "__main__":

    rec_store = SimilarItems()

    rec_store.load(
        "/home/mle-user/mle_projects/practicum_mle_4_recsys/similar_items.parquet",
        columns=["item_id_1", "item_id_2", "score"],
    )

    print(rec_store.get(item_id=17245, k=5))
    print(rec_store.get(item_id="default", k=5))
