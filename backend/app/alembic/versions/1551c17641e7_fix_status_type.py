"""fix status type

Revision ID: 1551c17641e7
Revises: 1a8e1033b0c1
Create Date: 2025-03-21 23:38:46.143857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1551c17641e7'
down_revision: Union[str, None] = '1a8e1033b0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
