"""use trigger func to create trigger for checking authors

Revision ID: d2c3cd3b7d9f
Revises: 324e2c57e20a
Create Date: 2024-01-12 16:04:47.029821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision: str = 'd2c3cd3b7d9f'
down_revision: Union[str, None] = '324e2c57e20a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    public_book_author_association_check_authors_trigger = PGTrigger(
        schema="public",
        signature="check_authors_trigger",
        on_entity="public.book_author_association",
        is_constraint=False,
        definition='BEFORE INSERT ON public.book_author_association\n    FOR EACH ROW EXECUTE FUNCTION before_insert_book_check()'
    )
    op.create_entity(public_book_author_association_check_authors_trigger)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    public_book_author_association_check_authors_trigger = PGTrigger(
        schema="public",
        signature="check_authors_trigger",
        on_entity="public.book_author_association",
        is_constraint=False,
        definition='BEFORE INSERT ON public.book_author_association\n    FOR EACH ROW EXECUTE FUNCTION before_insert_book_check()'
    )
    op.drop_entity(public_book_author_association_check_authors_trigger)

    # ### end Alembic commands ###