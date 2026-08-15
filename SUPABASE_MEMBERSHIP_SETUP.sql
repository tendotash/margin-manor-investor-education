-- MARGIN MANOR V7.2 — SUPABASE MEMBER ACCESS
-- Run once in Supabase Dashboard -> SQL Editor

create table if not exists public.memberships (
    user_id uuid primary key references auth.users(id) on delete cascade,
    email text not null,
    display_name text,
    plan text not null default 'Premium',
    status text not null default 'active'
        check (status in ('active', 'inactive', 'cancelled', 'suspended')),
    expires_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.memberships enable row level security;

drop policy if exists "Members can read their own membership" on public.memberships;

create policy "Members can read their own membership"
on public.memberships
for select
to authenticated
using (auth.uid() = user_id);

-- Do NOT add INSERT/UPDATE/DELETE policies for normal members.
