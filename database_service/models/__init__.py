import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

engine = create_engine(
    os.getenv("DB_URL", "postgresql://postgresql:root@localhost/online_shop")
)

Base = declarative_base()
