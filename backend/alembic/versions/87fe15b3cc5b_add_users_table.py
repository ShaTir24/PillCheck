"""add users table

Revision ID: 87fe15b3cc5b
Revises: c8613139036b
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '87fe15b3cc5b'
down_revision: Union[str, None] = 'c8613139036b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('token_version', sa.Integer(), nullable=False),
        sa.Column('password_reset_token_hash', sa.String(length=64), nullable=True),
        sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.add_column('profiles', sa.Column('user_id', sa.UUID(), nullable=False))
    op.create_index(op.f('ix_profiles_user_id'), 'profiles', ['user_id'], unique=False)
    op.create_foreign_key(
        'fk_profiles_user_id_users', 'profiles', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_profiles_user_id_users', 'profiles', type_='foreignkey')
    op.drop_index(op.f('ix_profiles_user_id'), table_name='profiles')
    op.drop_column('profiles', 'user_id')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
