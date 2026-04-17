"""initial schema: pessoa, grupo, atividade, assunto_*, feriado, parametro, etl_run

Revision ID: 20260417_1200
Revises:
Create Date: 2026-04-17 12:00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260417_1200"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "grupo",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(120), nullable=False, unique=True),
    )

    op.create_table(
        "pessoa",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("nome", sa.String(180), nullable=False, unique=True),
        sa.Column("email", sa.String(180), nullable=True),
        sa.Column(
            "grupo_id",
            sa.Integer(),
            sa.ForeignKey("grupo.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    op.create_table(
        "atividade",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("pasta", sa.String(60), nullable=True),
        sa.Column("assunto", sa.String(240), nullable=True),
        sa.Column("status", sa.String(60), nullable=True),
        sa.Column("data", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_prazo_fatal", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_conclusao", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "responsavel_id",
            sa.BigInteger(),
            sa.ForeignKey("pessoa.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "concluido_por_id",
            sa.BigInteger(),
            sa.ForeignKey("pessoa.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "responsavel_ativ_principal_id",
            sa.BigInteger(),
            sa.ForeignKey("pessoa.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("assunto_ativ_principal", sa.String(240), nullable=True),
        sa.Column("aproveitamento", sa.String(120), nullable=True),
        sa.Column("tipo_processo", sa.String(120), nullable=True),
        sa.Column("raw_json", JSONB, nullable=True),
        sa.Column(
            "coletado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_index("idx_ativ_status_data", "atividade", ["status", "data_conclusao"])
    op.create_index("idx_ativ_responsavel", "atividade", ["concluido_por_id", "data_conclusao"])
    op.create_index("idx_ativ_assunto", "atividade", ["assunto"])

    op.create_table(
        "pontuacao_ranking",
        sa.Column(
            "grupo_id",
            sa.Integer(),
            sa.ForeignKey("grupo.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("assunto_norm", sa.String(240), primary_key=True),
        sa.Column("pontos", sa.Integer(), nullable=False),
    )

    op.create_table(
        "assunto_excluido",
        sa.Column(
            "grupo_id",
            sa.Integer(),
            sa.ForeignKey("grupo.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=True,
        ),
        sa.Column("assunto_norm", sa.String(240), primary_key=True),
        sa.Column("motivo", sa.String(240), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    op.create_table(
        "assunto_permitido",
        sa.Column(
            "grupo_id",
            sa.Integer(),
            sa.ForeignKey("grupo.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("assunto_norm", sa.String(240), primary_key=True),
    )

    op.create_table(
        "feriado",
        sa.Column("data", sa.Date(), primary_key=True),
        sa.Column("descricao", sa.String(120), nullable=True),
    )

    op.create_table(
        "parametro",
        sa.Column("chave", sa.String(120), primary_key=True),
        sa.Column("valor", JSONB, nullable=False),
    )

    op.create_table(
        "etl_run",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fim", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("detalhes", JSONB, nullable=True),
    )

    # Placeholders para as materialized views (o ETL cria/refresha).
    # Criamos como VIEW vazias para os SELECTs funcionarem antes da primeira coleta.
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_produtividade AS
        SELECT
            ''::text AS responsavel,
            ''::text AS grupo,
            ''::text AS mes_ano,
            NULL::text AS quinzena,
            0::bigint AS total_concluidas,
            0::bigint AS total_atribuidas,
            0.0::float AS taxa_conclusao,
            0::bigint AS prazos_no_prazo,
            0::bigint AS prazos_em_atraso,
            0.0::float AS atividades_por_dia_util
        WHERE FALSE
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_produtividade ON mv_produtividade (responsavel, mes_ano)"
    )

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ranking AS
        SELECT
            0::int AS posicao,
            ''::text AS responsavel,
            ''::text AS grupo,
            0.0::float AS pontos_totais,
            0::bigint AS total_atividades,
            0.0::float AS aproveitamento_medio,
            ''::text AS mes_ano
        WHERE FALSE
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_ranking ON mv_ranking (responsavel, mes_ano)"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_ranking")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_produtividade")
    op.drop_table("etl_run")
    op.drop_table("parametro")
    op.drop_table("feriado")
    op.drop_table("assunto_permitido")
    op.drop_table("assunto_excluido")
    op.drop_table("pontuacao_ranking")
    op.drop_index("idx_ativ_assunto", table_name="atividade")
    op.drop_index("idx_ativ_responsavel", table_name="atividade")
    op.drop_index("idx_ativ_status_data", table_name="atividade")
    op.drop_table("atividade")
    op.drop_table("pessoa")
    op.drop_table("grupo")
