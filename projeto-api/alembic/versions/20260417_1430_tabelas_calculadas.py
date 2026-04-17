"""tabelas calculadas substituem MVs placeholder

Revision ID: 20260417_1430
Revises: 20260417_1200
Create Date: 2026-04-17 14:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260417_1430"
down_revision: str | None = "20260417_1200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Remover MVs placeholder criadas na migration anterior.
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_ranking CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_produtividade CASCADE")

    op.create_table(
        "produtividade_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("responsavel", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("natureza", sa.String(60), nullable=False, server_default=""),
        sa.Column("assunto", sa.String(240), nullable=False, server_default=""),
        sa.Column("grupo", sa.String(120), nullable=True),
        sa.Column("quinzena", sa.String(2), nullable=False),
        sa.Column("total_concluidas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("concluidas_dias_uteis", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dias_uteis_periodo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("media_diaria", sa.Float(), nullable=False, server_default="0"),
        sa.Column("no_prazo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fora_do_prazo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taxa_prazo_pct", sa.Float(), nullable=True),
        sa.Column(
            "calculado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.UniqueConstraint(
            "responsavel", "mes_ano", "natureza", "quinzena", "assunto",
            name="ux_produtividade",
        ),
    )
    op.create_index("idx_prod_mes", "produtividade_calculada", ["mes_ano"])
    op.create_index("idx_prod_grupo", "produtividade_calculada", ["grupo", "mes_ano"])

    op.create_table(
        "aproveitamento_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("responsavel", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("natureza", sa.String(60), nullable=False, server_default=""),
        sa.Column("assunto", sa.String(240), nullable=False, server_default=""),
        sa.Column("grupo", sa.String(120), nullable=True),
        sa.Column("sem_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("com_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("com_acrescimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("com_ressalva_e_acrescimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sem_aproveitamento", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_revisoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontuacao_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontuacao_maxima", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taxa_aproveitamento_pct", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "calculado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.UniqueConstraint(
            "responsavel", "mes_ano", "natureza", "assunto", name="ux_aproveitamento",
        ),
    )

    op.create_table(
        "aproveitamento_individual_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("avaliado", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("sem_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("com_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("com_acrescimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ressalva_acrescimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sem_aproveitamento", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taxa_pct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "calculado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.UniqueConstraint("avaliado", "mes_ano", name="ux_aprov_individual"),
    )

    op.create_table(
        "aproveitamento_peticao_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "responsavel_atividade_principal", sa.String(180), nullable=False,
        ),
        sa.Column("mes_ano", sa.String(16), nullable=False),
        sa.Column("revisao_sem_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revisao_com_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revisao_com_acrescimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revisao_ressalva_acrescimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revisao_sem_aproveitamento", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_revisoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "media_aproveitamento_pct", sa.Float(), nullable=False, server_default="0",
        ),
        sa.Column("revisores", sa.String(500), nullable=True),
        sa.Column("assunto_mais_frequente", sa.String(240), nullable=True),
        sa.Column(
            "calculado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.UniqueConstraint(
            "responsavel_atividade_principal", "mes_ano", name="ux_aprov_peticao",
        ),
    )

    op.create_table(
        "desempenho_revisor_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("revisor", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("total_revisoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sem_ressalva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("com_correcao", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taxa_correcao_pct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assunto_mais_corrigido", sa.String(240), nullable=True),
        sa.Column(
            "qtd_assunto_mais_corrigido", sa.Integer(), nullable=False, server_default="0",
        ),
        sa.Column(
            "calculado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.UniqueConstraint("revisor", "mes_ano", name="ux_desempenho_revisor"),
    )

    op.create_table(
        "ranking_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("responsavel", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("grupo", sa.String(120), nullable=True),
        sa.Column("posicao", sa.Integer(), nullable=False),
        sa.Column("pontos_brutos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontos_validos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_atividades", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taxa_aprov", sa.Float(), nullable=False, server_default="100"),
        sa.Column(
            "calculado_em", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.UniqueConstraint("responsavel", "mes_ano", name="ux_ranking"),
    )
    op.create_index("idx_ranking_mes", "ranking_calculada", ["mes_ano", "posicao"])

    op.create_table(
        "distribuicao_horario_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("responsavel", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("hora", sa.Integer(), nullable=False),
        sa.Column("contagem", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("responsavel", "mes_ano", "hora", name="ux_dist_horario"),
    )

    op.create_table(
        "distribuicao_assunto_calculada",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("responsavel", sa.String(180), nullable=False),
        sa.Column("mes_ano", sa.String(7), nullable=False),
        sa.Column("assunto", sa.String(240), nullable=False),
        sa.Column("contagem", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "responsavel", "mes_ano", "assunto", name="ux_dist_assunto",
        ),
    )


def downgrade() -> None:
    op.drop_table("distribuicao_assunto_calculada")
    op.drop_table("distribuicao_horario_calculada")
    op.drop_index("idx_ranking_mes", table_name="ranking_calculada")
    op.drop_table("ranking_calculada")
    op.drop_table("desempenho_revisor_calculada")
    op.drop_table("aproveitamento_peticao_calculada")
    op.drop_table("aproveitamento_individual_calculada")
    op.drop_table("aproveitamento_calculada")
    op.drop_index("idx_prod_grupo", table_name="produtividade_calculada")
    op.drop_index("idx_prod_mes", table_name="produtividade_calculada")
    op.drop_table("produtividade_calculada")
