"""add issue and constraints

Revision ID: cc53c52f7a4a
Revises: 472298a734f9
Create Date: 2026-10-01 20:47:33.201558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc53c52f7a4a'
down_revision: Union[str, Sequence[str], None] = '472298a734f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. First add the unique constraint to 'user' so 'issue' can reference it
    op.create_unique_constraint('uq_user_id_role', 'user', ['id', 'role'])

    # 2. Create the 'issue' table
    op.create_table('issue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('category', sa.Enum('ELECTRICITY', 'WATER', 'INTERNET', 'CLASSROOM', 'HOSTEL', 'CLEANLINESS', 'EQUIPMENT', 'OTHER', name='issue_category'), nullable=False),
    sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='issue_priority'), nullable=False),
    sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'ASSIGNED', 'RESOLVED', 'CLOSED', name='issue_status'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('assigned_employee_id', sa.Integer(), nullable=False),
    sa.Column('assigned_role', sa.Enum('STUDENT', 'FACULTY', 'STAFF', 'ADMIN', name='user_role', create_type=False), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("assigned_role = 'STAFF'", name='check_staff_role_only'),
    sa.ForeignKeyConstraint(['assigned_employee_id', 'assigned_role'], ['user.id', 'user.role'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # 3. Create the 'staff' table
    op.create_table('staff',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('total_jobs', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    op.drop_table('staff')
    op.drop_table('issue')
    op.drop_constraint('uq_user_id_role', 'user', type_='unique')

