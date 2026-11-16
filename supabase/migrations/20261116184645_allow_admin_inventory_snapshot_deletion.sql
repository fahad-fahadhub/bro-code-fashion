-- Allow active BCF owners and managers to remove a current inventory snapshot.
-- Historical inventory movements remain append-only for auditability.
grant delete on table public.inventory to authenticated;

drop policy if exists "BCF managers delete inventory" on public.inventory;
create policy "BCF managers delete inventory"
  on public.inventory for delete to authenticated
  using (private.can_manage_catalog());
