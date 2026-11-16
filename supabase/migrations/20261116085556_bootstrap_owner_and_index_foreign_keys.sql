-- Bootstrap the sole existing Supabase Auth user as BCF owner.
-- Adds indexes recommended by the Supabase performance advisor.

do $$
declare
  auth_user_count integer;
  owner_user_id uuid;
begin
  select count(*) into auth_user_count from auth.users;
  if auth_user_count <> 1 then
    raise exception 'Expected exactly one Supabase Auth user for initial BCF owner setup; found %', auth_user_count;
  end if;

  select id into owner_user_id from auth.users limit 1;

  insert into public.admin_users (user_id, full_name, role, is_active)
  values (owner_user_id, 'Bro Code Fashion Owner', 'owner', true)
  on conflict (user_id) do update
    set full_name = excluded.full_name,
        role = 'owner',
        is_active = true;
end $$;

create index if not exists idx_inventory_movements_performed_by
  on public.inventory_movements(performed_by);
create index if not exists idx_order_items_product_id
  on public.order_items(product_id);
create index if not exists idx_order_items_variant_id
  on public.order_items(variant_id);
create index if not exists idx_orders_customer_id
  on public.orders(customer_id);
