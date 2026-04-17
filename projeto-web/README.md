# projeto-web — Dashboard FG Frontend

React 18 + Vite 6 + TypeScript + TanStack Query + Tailwind + Recharts.

## Dev

```bash
npm install
npm run dev        # http://localhost:5173 — proxy para API em :8080
```

## Build

```bash
npm run typecheck
npm run build      # dist/
npm run preview
```

## Gerar tipos da API

Com a API rodando em `localhost:8080`:

```bash
npm run openapi:pull
```

Sobrescreve `src/api/types.ts`.

## Lint / Format

```bash
npm run lint
npm run format
```

## Estrutura

```
src/
├── main.tsx             bootstrap
├── App.tsx              rotas (Protected, login, dashboard, ranking)
├── api/
│   ├── client.ts        axios withCredentials
│   └── types.ts         tipos (regeráveis via openapi-typescript)
├── hooks/               useAuth, useDashboard, useRanking
├── components/          AppShell, KpiCard, FiltersBar, tabelas, charts
├── routes/              Dashboard, Ranking, Login
├── lib/                 formatters, theme
└── styles.css           Tailwind + components customizados
```

## Deploy

Ver `../.claude/skills/deploy-web/SKILL.md`.
