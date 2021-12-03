"""empty message

Revision ID: d957edb6abfa
Revises: 
Create Date: 2021-12-03 11:47:16.085106

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd957edb6abfa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tbl_state')
    op.drop_table('customers')
    op.alter_column('guest', 'stateid',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_foreign_key(None, 'guest', 'state', ['stateid'], ['state_id'])
    op.create_foreign_key(None, 'guest_gift', 'guest', ['guest_id'], ['id'])
    op.create_foreign_key(None, 'guest_gift', 'gift', ['gift_id'], ['id'])
    op.alter_column('lga', 'state_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    op.create_foreign_key(None, 'lga', 'state', ['state_id'], ['state_id'])
    op.create_foreign_key(None, 'question', 'guest', ['guest_id'], ['id'])
    op.create_foreign_key(None, 'transaction', 'guest', ['trx_guestid'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_constraint(None, 'question', type_='foreignkey')
    op.drop_constraint(None, 'lga', type_='foreignkey')
    op.alter_column('lga', 'state_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.drop_constraint(None, 'guest_gift', type_='foreignkey')
    op.drop_constraint(None, 'guest_gift', type_='foreignkey')
    op.drop_constraint(None, 'guest', type_='foreignkey')
    op.alter_column('guest', 'stateid',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.create_table('customers',
    sa.Column('cust_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('cust_fname', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('cust_lname', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('cust_dob', sa.DATE(), nullable=False),
    sa.Column('cust_phone', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('cust_city', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('cust_id'),
    comment='This table stores the information about our customers',
    mysql_comment='This table stores the information about our customers',
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('tbl_state',
    sa.Column('state_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('state_name', mysql.VARCHAR(length=20), server_default=sa.text("''"), nullable=False),
    sa.PrimaryKeyConstraint('state_id'),
    mysql_default_charset='utf8',
    mysql_engine='MyISAM'
    )
    # ### end Alembic commands ###
