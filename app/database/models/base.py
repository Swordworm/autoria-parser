from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData(schema="public")
Base = declarative_base(metadata=metadata)
