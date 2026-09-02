"""change Items_Order.amount column to integer

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "Items_Order", "amount",
        existing_type=sa.String(), type_=sa.Integer(),
        existing_nullable=True, postgresql_using="amount::integer",
    )


def downgrade() -> None:
    op.alter_column(
        "Items_Order", "amount",
        existing_type=sa.Integer(), type_=sa.String(),
        existing_nullable=True,
    )