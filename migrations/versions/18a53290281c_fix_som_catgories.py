"""fix som catgories

Revision ID: 18a53290281c
Revises: 1a8b82c1a5d2
Create Date: 2024-08-23 14:11:27.504283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18a53290281c'
down_revision = '1a8b82c1a5d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recurring_expense')
    op.drop_table('category')
    op.drop_table('expenses')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_email')

    op.drop_table('user')
    op.drop_table('notification')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('message', sa.VARCHAR(length=255), nullable=False),
    sa.Column('type', sa.VARCHAR(length=50), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('is_read', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(length=128), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_name')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('ix_user_email', ['email'], unique=1)

    op.create_table('expenses',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('amount', sa.FLOAT(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), nullable=False),
    sa.Column('date', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('category_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('category',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('recurring_expense',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('amount', sa.FLOAT(), nullable=False),
    sa.Column('type_expense', sa.VARCHAR(length=255), nullable=False),
    sa.Column('description_expense', sa.VARCHAR(length=255), nullable=False),
    sa.Column('recurrence', sa.VARCHAR(length=255), nullable=False),
    sa.Column('start_date', sa.DATETIME(), nullable=False),
    sa.Column('end_date', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('category_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
