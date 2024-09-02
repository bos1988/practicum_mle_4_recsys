import pandas as pd


def show_dtypes(df: pd.DataFrame, samples:int = 3) -> pd.DataFrame:
    return pd.merge(
        df.dtypes.astype(str).to_frame(name="type").reset_index().sort_values("type"),
        df.isna().sum().to_frame(name="isna").reset_index()
    ).merge(
        df.head(samples).T.reset_index()
    )
