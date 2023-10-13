from sqlalchemy import Engine, create_engine


def get_engine(db_url: str) -> Engine:
    return create_engine(url=db_url)
