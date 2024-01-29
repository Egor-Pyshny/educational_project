"""create book view & trigger func for checking authors

Revision ID: 324e2c57e20a
Revises: 63f9da1020ec
Create Date: 2024-01-12 15:57:34.814185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text
from alembic_utils.pg_materialized_view import PGMaterializedView
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision: str = '324e2c57e20a'
down_revision: Union[str, None] = '63f9da1020ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    public_catalogue_book_materializedview = PGMaterializedView(
                schema="public",
                signature="catalogue_book_materializedview",
                definition="SELECT b.book_id, b.book_title, b.book_price, STRING_AGG(a.author_name, ', ') AS authors\n    FROM books b\n    JOIN book_author_association ba ON b.book_id = ba.book_id\n    JOIN authors a ON ba.author_id = a.author_id\n    GROUP BY b.book_id, b.book_title, b.book_amount",
                with_data=True
            )

    op.create_entity(public_catalogue_book_materializedview)

    public_before_insert_book_check = PGFunction(
        schema="public",
        signature="before_insert_book_check()",
        definition="RETURNS TRIGGER AS $$\n    BEGIN\n        IF NOT EXISTS (SELECT 1 FROM book_author_association WHERE author_id = NEW.author_id) THEN\n            RAISE EXCEPTION 'Несуществующий ID автора --> %', NEW.author_id USING HINT = 'Проверьте ваш ID автора';\n        END IF;\n        RETURN NEW;\n    END; $$ language 'plpgsql'"
    )
    op.create_entity(public_before_insert_book_check)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    public_before_insert_book_check = PGFunction(
        schema="public",
        signature="before_insert_book_check()",
        definition="RETURNS TRIGGER AS $$\n    BEGIN\n        IF NOT EXISTS (SELECT 1 FROM book_author_association WHERE author_id = NEW.author_id) THEN\n            RAISE EXCEPTION 'Несуществующий ID автора --> %', NEW.author_id USING HINT = 'Проверьте ваш ID автора';\n        END IF;\n        RETURN NEW;\n    END; $$ language 'plpgsql'"
    )
    op.drop_entity(public_before_insert_book_check)

    public_catalogue_book_materializedview = PGMaterializedView(
                schema="public",
                signature="catalogue_book_materializedview",
                definition="SELECT b.book_id, b.book_title, b.book_price, STRING_AGG(a.author_name, ', ') AS authors\n    FROM books b\n    JOIN book_author_association ba ON b.book_id = ba.book_id\n    JOIN authors a ON ba.author_id = a.author_id\n    GROUP BY b.book_id, b.book_title, b.book_amount",
                with_data=True
            )

    op.drop_entity(public_catalogue_book_materializedview)

    # ### end Alembic commands ###
