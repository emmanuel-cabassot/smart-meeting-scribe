"""Initial migration - Create all tables with organization support

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === SERVICE TABLE ===
    op.create_table(
        'service',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_id'), 'service', ['id'], unique=False)
    op.create_index(op.f('ix_service_name'), 'service', ['name'], unique=True)

    # === PROJECT TABLE ===
    op.create_table(
        'project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_id'), 'project', ['id'], unique=False)
    op.create_index(op.f('ix_project_name'), 'project', ['name'], unique=True)

    # === USER TABLE ===
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)

    # === MEETING TABLE ===
    op.create_table(
        'meeting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('s3_path', sa.String(1000), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_confidential', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meeting_id'), 'meeting', ['id'], unique=False)
    op.create_index(op.f('ix_meeting_status'), 'meeting', ['status'], unique=False)
    op.create_index(op.f('ix_meeting_title'), 'meeting', ['title'], unique=False)

    # === USER <-> PROJECT ASSOCIATION TABLE ===
    op.create_table(
        'user_project_link',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'project_id')
    )

    # === MEETING <-> PROJECT ASSOCIATION TABLE ===
    op.create_table(
        'meeting_project_link',
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meeting.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('meeting_id', 'project_id')
    )


def downgrade() -> None:
    op.drop_table('meeting_project_link')
    op.drop_table('user_project_link')
    op.drop_index(op.f('ix_meeting_title'), table_name='meeting')
    op.drop_index(op.f('ix_meeting_status'), table_name='meeting')
    op.drop_index(op.f('ix_meeting_id'), table_name='meeting')
    op.drop_table('meeting')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_project_name'), table_name='project')
    op.drop_index(op.f('ix_project_id'), table_name='project')
    op.drop_table('project')
    op.drop_index(op.f('ix_service_name'), table_name='service')
    op.drop_index(op.f('ix_service_id'), table_name='service')
    op.drop_table('service')
