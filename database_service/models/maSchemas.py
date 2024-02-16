from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import Session

from models.author_book_models import Authors, Books


class AuthorsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Authors
        load_instance = True


class BooksSchema(SQLAlchemyAutoSchema):
    book_authors = fields.Nested(AuthorsSchema, many=True)

    class Meta:
        model = Books


