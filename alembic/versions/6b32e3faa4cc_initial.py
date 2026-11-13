"""initial

Revision ID: 6b32e3faa4cc
Revises: 
Create Date: 2026-10-26 22:22:46.864294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b32e3faa4cc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.String(length=1024), nullable=False),
        sa.Column("likes_count", sa.Integer(), nullable=False),
        sa.CheckConstraint("likes_count >= 0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "post_likes",
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("post_likes")
    op.drop_table("posts")
