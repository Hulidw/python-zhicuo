-- 在 Supabase SQL Editor 中运行一次；开启 Email provider 与邮箱确认。
create table if not exists public.learning_state (
  user_id uuid primary key references auth.users(id) on delete cascade,
  data jsonb not null default '{"records":[],"mistakes":{},"session":null}',
  revision integer not null default 1 check (revision > 0),
  constraint data_size check (octet_length(data::text) <= 5000000)
);
alter table public.learning_state enable row level security;
revoke all on public.learning_state from anon;
grant select, insert, update on public.learning_state to authenticated;
create policy "Read own learning state" on public.learning_state for select to authenticated using ((select auth.uid()) = user_id);
create policy "Insert own learning state" on public.learning_state for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Update own learning state" on public.learning_state for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
