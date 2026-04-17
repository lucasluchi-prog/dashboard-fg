-- Inicialização do Postgres local via docker-compose.
-- Alembic cuida do schema; aqui só garantimos extensões úteis.
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
