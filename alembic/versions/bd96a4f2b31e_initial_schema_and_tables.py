"""Initial schema and tables

Revision ID: bd96a4f2b31e
Revises:
Create Date: 2023-03-03 13:37:23.190828

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bd96a4f2b31e"  # pragma: allowlist secret
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("create schema pttbackend")

    op.create_table(
        "pttinstances",
        sa.Column("ownerid", sa.Unicode(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("grouping", sa.Unicode(), nullable=False),
        sa.Column("tfcompleted", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tfinputs", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("tfoutputs", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("pk", postgresql.UUID(), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("pk"),
        schema="pttbackend",
    )
    op.create_index(
        op.f("ix_pttbackend_pttinstances_color"), "pttinstances", ["color"], unique=False, schema="pttbackend"
    )
    op.create_index(
        op.f("ix_pttbackend_pttinstances_grouping"), "pttinstances", ["grouping"], unique=False, schema="pttbackend"
    )
    op.create_index(
        op.f("ix_pttbackend_pttinstances_ownerid"), "pttinstances", ["ownerid"], unique=False, schema="pttbackend"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_pttbackend_pttinstances_ownerid"), table_name="pttinstances", schema="pttbackend")
    op.drop_index(op.f("ix_pttbackend_pttinstances_grouping"), table_name="pttinstances", schema="pttbackend")
    op.drop_index(op.f("ix_pttbackend_pttinstances_color"), table_name="pttinstances", schema="pttbackend")
    op.drop_table("pttinstances", schema="pttbackend")

    op.execute("drop schema pttbackend")

    # ### end Alembic commands ###
