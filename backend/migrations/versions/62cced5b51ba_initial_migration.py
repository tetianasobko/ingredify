"""Initial migration

Revision ID: 62cced5b51ba
Revises: 
Create Date: 2025-02-24 17:43:27.772578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62cced5b51ba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredient_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('source', sa.String(length=500), nullable=True),
    sa.Column('steps', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipe_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ingredient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['ingredient_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipe_type_association',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['recipe_type.id'], ),
    sa.PrimaryKeyConstraint('recipe_id', 'type_id')
    )
    op.create_table('recipe_ingredient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe_ingredient')
    op.drop_table('recipe_type_association')
    op.drop_table('ingredient')
    op.drop_table('recipe_type')
    op.drop_table('recipe')
    op.drop_table('ingredient_category')
    # ### end Alembic commands ###
