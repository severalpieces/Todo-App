"""Create phone number for user column

Revision ID: 951972e0a7aa
Revises: 
Create Date: 2025-02-04 19:09:04.694722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '951972e0a7aa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone_number")
