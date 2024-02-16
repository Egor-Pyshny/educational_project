import asyncio
import json

import logging
from typing import Dict

from sqlalchemy import select, delete, desc, Table, text
from sqlalchemy.schema import MetaData
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base
from models.author_book_models import Books, Authors, catalogue_view
from utils.LoggerFormater import CustomFormatter


class Core:
    def __init__(self):
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
        self.db_logger = logging.getLogger("DBCore")
        self.db_error_logger = logging.getLogger("DBCore error")
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(CustomFormatter(fmt))
        self.db_logger.setLevel(logging.INFO)
        self.db_logger.addHandler(stdout_handler)
        self.db_error_logger.setLevel(logging.ERROR)
        self.db_error_logger.addHandler(stdout_handler)

    async def catalog_add_func(self, body) -> Dict[str, str]:
        self.db_error_logger.error("test")
        try:
            async with self.custom_session() as my_session:
                async with my_session.begin():
                    data = json.loads(body)["data"]
                    authors_list = []
                    for author_data in data["book_authors"]:
                        query = select(Authors).where(
                            Authors.author_name == author_data["author_name"]).where(
                            Authors.author_surname == author_data["author_surname"])
                        self.db_logger.info(query)
                        res = await my_session.execute(query)
                        author = res.scalar_one_or_none()
                        if author is None:
                            author = Authors(
                                author_name=author_data["author_name"],
                                author_surname=author_data["author_surname"]
                            )
                        authors_list.append(author)
                    new_book = Books(
                        book_title=data["book_title"],
                        book_amount=data["book_amount"],
                        book_description=data["book_description"],
                        book_price=data["book_price"],
                        book_authors=authors_list
                    )
                    # new_book.book_authors.append(authors_list)
                    my_session.add(new_book)
                    return json.dumps({"res":"completed","exception":""})
        except IntegrityError as e:
            self.db_error_logger.error(e.args[0])
            return json.dumps({"res":"exception","exception":e.args[0]})

    async def catalog_remove_func(self, body) -> Dict[str, str]:
        async with self.custom_session() as my_session:
            async with my_session.begin():
                data = json.loads(body)["data"]
                stmt = delete(Books).where(Books.book_title == data["book_title"])
                self.db_logger.info(stmt)
                res = await my_session.execute(stmt)
                # res.rowcount = 0 таких книг нет
                return json.dumps({"res": "completed", "exception": ""})

    async def catalog_list_func(self, body) -> Dict[str, str]:
        try:
            async with self.custom_session() as my_session:
                async with my_session.begin():
                    data = json.loads(body)["data"]
                    async with self.engine.begin() as conn:
                        MaterializedView = await conn.run_sync(
                            lambda conn: Table('catalogue_book_materializedview', MetaData(), autoload_with=conn)
                        )
                    order_column = MaterializedView.c[data.get("filter_field","book_title")]
                    if data.get("filter_direction","asc").lower() == "desc":
                        order_column = desc(order_column)
                    stmt = select(MaterializedView).offset(int(data.get("page",0))*20).limit(20).order_by(order_column)
                    self.db_logger.info(stmt)
                    res = await my_session.execute(stmt)
                    books = res.fetchall()
                    response = []
                    keys = ["book_id", "book_title", "book_price", "book_authors_surname"]
                    for book in books:
                        temp = {keys[i]: v for i, v in enumerate(book)}
                        response.append(temp)
                    return json.dumps({"res": str(response), "exception": ""})
        except KeyError as e:
            if e.args[0] == "data":
                self.db_error_logger.error(f"no column {e.args[0]}")
                raise e
            else:
                self.db_error_logger.error(f"no such column as {e.args[0]}, possible columns: {MaterializedView.c}")
                return json.dumps({"res": "exception", "exception": f"no such column as {e.args[0]}, possible columns: {MaterializedView.c}"})


# c = Core()
# b = """{"data":{
#         "book_title":"0",
#         "book_amount":1,
#         "book_description":"description",
#         "book_price": 1.0,
#         "fiter_field":"book_thgitle",
#         "filter_direction":"ASC",
#         "page":0,
#         "book_authors":[
#             {
#                 "author_name":"a3",
#                 "author_surname":"s3"
#             }
#         ]
#     }}"""
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(c.catalog_list_func(b))
