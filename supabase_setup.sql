-- Apontamento de Produção -- rode isto uma vez no SQL Editor do Supabase
-- (Project > SQL Editor > New query > cola isto > Run).

create table if not exists apontamentos (
  id uuid primary key default gen_random_uuid(),
  ordem text not null,
  lider_inicio text,
  inicio timestamptz not null default now(),
  lider_termino text,
  termino timestamptz,
  created_at timestamptz not null default now()
);

alter table apontamentos enable row level security;

-- a página usa a "anon key" (pública por natureza no Supabase) pra ler e
-- gravar nesta tabela -- por isso essas políticas liberam select/insert/update
-- pra ela. Ninguém de fora enxerga outras tabelas nem consegue apagar linhas.
create policy "apontamentos_select" on apontamentos
  for select using (true);

create policy "apontamentos_insert" on apontamentos
  for insert with check (true);

create policy "apontamentos_update" on apontamentos
  for update using (true);
