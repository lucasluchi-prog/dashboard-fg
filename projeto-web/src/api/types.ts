// Tipos esqueleto. Em tempo de dev, regerar via `npm run openapi:pull`
// contra o /openapi.json da API rodando em localhost:8080.

export type User = {
  email: string;
  name: string;
  picture?: string | null;
  hd?: string | null;
};

export type ProdutividadeItem = {
  responsavel: string;
  grupo: string;
  mes_ano: string;
  quinzena?: string | null;
  total_concluidas: number;
  total_atribuidas: number;
  taxa_conclusao: number;
  prazos_no_prazo: number;
  prazos_em_atraso: number;
  atividades_por_dia_util: number;
};

export type RankingItem = {
  posicao: number;
  responsavel: string;
  grupo: string;
  pontos_totais: number;
  total_atividades: number;
  aproveitamento_medio: number;
  mes_ano: string;
};

export type AproveitamentoItem = {
  responsavel: string;
  grupo: string;
  mes_ano: string;
  aproveitamento_medio: number;
  total_revisadas: number;
  sem_ressalva: number;
  com_ressalva: number;
  com_acrescimo: number;
  com_ressalva_e_acrescimo: number;
  sem_aproveitamento: number;
};

export type DashboardData = {
  produtividade: ProdutividadeItem[];
  aprovIndividual: Array<Record<string, unknown>>;
  aprovCalculado: AproveitamentoItem[];
  desempenhoRevisor: Array<Record<string, unknown>>;
  distribuicaoHorario: Array<Record<string, unknown>>;
  distribuicaoAssunto: Array<Record<string, unknown>>;
  rankingGamificado: RankingItem[];
  updatedAt: string;
};
