-- Allow active BCF owners and managers to create and adjust stock.
grant select, insert, update on table public.inventory to authenticated;

drop policy if exists "BCF managers insert inventory" on public.inventory;
create policy "BCF managers insert inventory"
  on public.inventory for insert to authenticated
  with check (private.can_manage_catalog());

drop policy if exists "BCF managers update inventory" on public.inventory;
create policy "BCF managers update inventory"
  on public.inventory for update to authenticated
  using (private.can_manage_catalog())
  with check (private.can_manage_catalog());

grant select, insert on table public.inventory_movements to authenticated;

drop policy if exists "BCF managers insert inventory movements" on public.inventory_movements;
create policy "BCF managers insert inventory movements"
  on public.inventory_movements for insert to authenticated
  with check (private.can_manage_catalog());
