"""msg

Revision ID: 8c86961b1f45
Revises: 494ce4eb5d52
Create Date: 2025-01-12 17:47:49.871343

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c86961b1f45"
down_revision: Union[str, None] = "494ce4eb5d52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("task", sa.Column("title", sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("task", "title")
    # ### end Alembic commands ###
