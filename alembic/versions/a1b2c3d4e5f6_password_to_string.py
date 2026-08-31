"""change users.password column to string

Revision ID: a1b2c3d4e5f6
Revises: 0adf3948641a
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "0adf3948641a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "password", existing_type=sa.Integer(),
                    type_=sa.String(), existing_nullable=True, nullable=False)


def downgrade() -> None:
    op.alter_column("users", "password", existing_type=sa.String(),
                    type_=sa.Integer(), existing_nullable=False, nullable=True)