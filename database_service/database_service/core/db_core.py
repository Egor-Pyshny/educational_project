import json

import logging

from sqlalchemy import select, delete, desc
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models.author_book_models import Books, Authors
from models.maSchemas import BooksSchema
from utils.LoggerFormater import CustomFormatter


class Core:
    def __init__(self):
        self.custom_session = None
        self.engine = None
        self.connection_pool = None
        self.db_logger = logging.getLogger("psycopg.pool")
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(CustomFormatter(fmt))
        self.db_logger.setLevel(logging.INFO)
        self.db_logger.addHandler(stdout_handler)

    async def initialize(self):
        db_url = 'postgresql+psycopg://postgres:postgres@localhost/online_shop'
        self.engine = create_async_engine(
            db_url,
            poolclass=AsyncAdaptedQueuePool,
            max_overflow=0,
            pool_size=10,
        )
        self.custom_session = sessionmaker(
            expire_on_commit=False,
            class_=AsyncSession,
            bind=self.engine,
        )
        self.db_logger.info("connection pool ready")

    async def catalog_add_func(self, body) -> str:
        try:
            async with self.custom_session() as my_session:
                async with my_session.begin():
                    data = json.loads(body.decode())["data"]
                    new_book = BooksSchema.load(data)
                    # authors_list = []
                    # for author in data["authors"]:
                    #     authors_list.append(Authors(
                    #         authr_name=author["name"],
                    #         author_surname=author["surname"]
                    #     ))
                    # new_book = Books(
                    #     book_title=data["title"],
                    #     book_amount=data["amount"],
                    #     book_description=data["description"],
                    #     book_price=data["price"],
                    # )
                    # new_book.book_authors.append(authors_list)
                    await my_session.add(new_book)
                    return json.dumps({"res":"added","exception":""})
        except NoResultFound as e:
            print(f"Книга с названием не найдена.")

    async def catalog_remove_func(self, body) -> str:
        try:
            async with self.custom_session() as my_session:
                async with my_session.begin():
                    data = json.loads(body.decode())["data"]
                    stmt = delete(Books).where(Books.title == data["title"])
                    await my_session.execute(stmt)
                    return json.dumps({"res": "deleted", "exception": ""})
        except NoResultFound as e:
            print(f"Книга с названием не найдена.")

    async def catalog_list_func(self, body):
        try:
            async with self.custom_session() as my_session:
                async with my_session.begin():
                    data = json.loads(body.decode())["data"]
                    stmt = select(Books).offset(int(data["page"])*20).limit(20).order_by(desc(Books.book_title))
                    books = my_session.execute(stmt)
        except NoResultFound:
            print(f"Книга с названием не найдена.")
