from uuid import uuid4

from alembic_utils.pg_materialized_view import PGMaterializedView
from alembic_utils.pg_trigger import PGTrigger
from alembic_utils.pg_function import PGFunction
from sqlalchemy import UUID
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from . import Base


book_author_association = Table(
    "book_author_association",
    Base.metadata,
    Column(
        "author_id",
        Integer,
        ForeignKey(
            "authors.author_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        primary_key=True,
    ),
    Column(
        "book_id",
        UUID,
        ForeignKey("books.book_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)


class Authors(Base):
    __tablename__ = "authors"

    author_id = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        index=True,
    )
    author_name = Column(String(25), nullable=False, default="NAME")
    author_surname = Column(String(25), nullable=False, default="SURNAME")
    author_books = relationship(
        "Books",
        secondary=book_author_association,
        back_populates="book_authors",
    )


class Books(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint(
            name="CHK_book_price_more_than_zero", sqltext="book_price > 0.0"
        ),
        CheckConstraint(
            name="CHK_book_amount_not_negative", sqltext="book_amount >= 0"
        ),
    )

    book_id = Column(UUID, primary_key=True, nullable=False, default=uuid4())
    book_title = Column(
        String(50), index=True, unique=True, nullable=False, default="NO TITLE"
    )
    book_amount = Column(SmallInteger, nullable=False, default=0)
    book_description = Column(Text, nullable=False, default="")
    book_price = Column(Float, nullable=False, default="1.0")
    book_authors = relationship(
        "Authors",
        secondary=book_author_association,
        back_populates="author_books",
        passive_deletes=True,
    )


before_insert_book_check = PGFunction(
    schema="public",
    signature="before_insert_book_check()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM authors WHERE author_id = NEW.author_id) THEN
            RAISE EXCEPTION 'Несуществующий ID автора --> %', NEW.author_id USING HINT = 'Проверьте ваш ID автора';
        END IF;
        RETURN NEW;
    END; $$ language 'plpgsql'
    """
)

# сначала нужно сделать таблицы
catalogue_view = PGMaterializedView(
    schema="public",
    signature="catalogue_book_materializedview",
    definition="""
    SELECT b.book_id, b.book_title, b.book_price, STRING_AGG(a.author_surname, ', ') AS authors
    FROM books b
    JOIN book_author_association ba ON b.book_id = ba.book_id
    JOIN authors a ON ba.author_id = a.author_id
    GROUP BY b.book_id, b.book_title, b.book_amount;
    """,
    with_data=True
)
# session commit сама делает транзакцию надо ловить исключение и делать rollback
book_author_association_before_insert_trigger = PGTrigger(
    schema="public",
    signature="check_authors_trigger",
    on_entity="public.books",
    definition="""
    BEFORE INSERT ON public.books
    FOR EACH ROW EXECUTE FUNCTION before_insert_book_check()
    """,
)
