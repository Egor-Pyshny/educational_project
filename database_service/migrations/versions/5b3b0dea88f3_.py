"""empty message

Revision ID: 5b3b0dea88f3
Revises: 0c8db1bb84fb
Create Date: 2024-02-01 14:22:24.906322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision: str = '5b3b0dea88f3'
down_revision: Union[str, None] = '0c8db1bb84fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    public_books_check_authors_trigger = PGTrigger(
        schema="public",
        signature="check_authors_trigger",
        on_entity="public.books",
        is_constraint=False,
        definition='BEFORE INSERT ON public.books FOR EACH ROW EXECUTE FUNCTION before_insert_book_check()'
    )
    op.drop_entity(public_books_check_authors_trigger)

    public_before_insert_book_check = PGFunction(
        schema="public",
        signature="before_insert_book_check()",
        definition="returns trigger\n LANGUAGE plpgsql\nAS $function$\n    BEGIN\n        IF NOT EXISTS (SELECT 1 FROM authors WHERE author_id = NEW.author_id) THEN\n            RAISE EXCEPTION 'Несуществующий ID автора --> %', NEW.author_id USING HINT = 'Проверьте ваш ID автора';\n        END IF;\n        RETURN NEW;\n    END; $function$"
    )
    op.drop_entity(public_before_insert_book_check)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    public_before_insert_book_check = PGFunction(
        schema="public",
        signature="before_insert_book_check()",
        definition="returns trigger\n LANGUAGE plpgsql\nAS $function$\n    BEGIN\n        IF NOT EXISTS (SELECT 1 FROM authors WHERE author_id = NEW.author_id) THEN\n            RAISE EXCEPTION 'Несуществующий ID автора --> %', NEW.author_id USING HINT = 'Проверьте ваш ID автора';\n        END IF;\n        RETURN NEW;\n    END; $function$"
    )
    op.create_entity(public_before_insert_book_check)

    public_books_check_authors_trigger = PGTrigger(
        schema="public",
        signature="check_authors_trigger",
        on_entity="public.books",
        is_constraint=False,
        definition='BEFORE INSERT ON public.books FOR EACH ROW EXECUTE FUNCTION before_insert_book_check()'
    )
    op.create_entity(public_books_check_authors_trigger)

    # ### end Alembic commands ###
