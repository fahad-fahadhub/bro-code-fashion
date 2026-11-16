-- Bro Code Fashion: harden the existing Supabase schema.
-- Existing tables were created before repository migrations were connected.
-- This migration preserves all existing records.

revoke all on function public.is_active_admin() from public;
revoke all on function public.is_active_admin() from anon;
grant execute on function public.is_active_admin() to authenticated;

revoke all privileges on table
  public.admin_users, public.customers, public.inventory,
  public.inventory_movements, public.order_items, public.orders,
  public.payments, public.product_images, public.product_variants, public.products
from anon;

grant select, insert, update, delete on table
  public.admin_users, public.customers, public.inventory,
  public.inventory_movements, public.order_items, public.orders,
  public.payments, public.product_images, public.product_variants, public.products
to authenticated;

grant select on table public.products, public.product_variants, public.product_images to anon;

drop policy if exists "Admins view admin users" on public.admin_users;
drop policy if exists "Admins view customers" on public.customers;
drop policy if exists "Admins view inventory" on public.inventory;
drop policy if exists "Admins view inventory movements" on public.inventory_movements;
drop policy if exists "Admins view order items" on public.order_items;
drop policy if exists "Admins update orders" on public.orders;
drop policy if exists "Admins view orders" on public.orders;
drop policy if exists "Admins view payments" on public.payments;
drop policy if exists "Admins manage product images" on public.product_images;
drop policy if exists "Admins manage variants" on public.product_variants;
drop policy if exists "Admins manage products" on public.products;
drop policy if exists "Public can view active product images" on public.product_images;
drop policy if exists "Public can view active variants" on public.product_variants;
drop policy if exists "Public can view active products" on public.products;

create policy "BCF active admins manage admin users" on public.admin_users
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage customers" on public.customers
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage inventory" on public.inventory
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage inventory movements" on public.inventory_movements
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage order items" on public.order_items
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage orders" on public.orders
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage payments" on public.payments
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage product images" on public.product_images
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage variants" on public.product_variants
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
create policy "BCF active admins manage products" on public.products
for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());

create policy "Public can view active products" on public.products
for select to anon using (status = 'active');
create policy "Public can view active variants" on public.product_variants
for select to anon using (
  is_active = true and exists (
    select 1 from public.products p
    where p.id = product_variants.product_id and p.status = 'active'
  )
);
create policy "Public can view active product images" on public.product_images
for select to anon using (
  exists (
    select 1 from public.products p
    where p.id = product_images.product_id and p.status = 'active'
  )
);
